import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .models import Cart
from tickets.models import Ticket
from tickets.utils import generate_invoice_pdf  # <--- Импорт генератора

User = get_user_model()

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Обработка успешной оплаты
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('metadata', {}).get('user_id')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                cart = Cart.objects.get(user=user)
                
                tickets_created = []
                
                for item in cart.items.all():
                    # 1. Создаем Тикет
                    ticket = Ticket.objects.create(
                        client=user,
                        service_name=item.service.name,
                        variant_name=item.variant.name if item.variant else None,
                        price_paid=item.get_price(),
                        user_note=f"Paid Service: {item.service.name}",
                        status='paid' 
                    )
                    
                    # 2. Генерируем PDF Инвойс и прикрепляем к тикету
                    try:
                        generate_invoice_pdf(ticket)
                    except Exception as e:
                        print(f"Error generating PDF for ticket #{ticket.ticket_number}: {e}")

                    tickets_created.append(ticket.ticket_number)

                # 3. Очищаем корзину
                cart.items.all().delete()
                
                # 4. Отправляем письмо-подтверждение
                send_mail(
                    subject="Order Confirmed - TESEO CAF",
                    message=f"Payment received.\nTicket(s) created: {', '.join(tickets_created)}\n\nPlease go to your dashboard to download your invoice and upload required documents.",
                    from_email=None,
                    recipient_list=[user.email],
                    fail_silently=True
                )
                
                print(f"Successfully processed order for {user.email}")
                
            except User.DoesNotExist:
                print("Webhook Error: User not found")
            except Cart.DoesNotExist:
                print("Webhook Error: Cart not found")

    return HttpResponse(status=200)