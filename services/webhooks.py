import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .models import Cart
# ВАЖНО: Импортируем Ticket из ПРАВИЛЬНОГО приложения
from tickets.models import Ticket 

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
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('metadata', {}).get('user_id')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                cart = Cart.objects.get(user=user)
                
                tickets_created = []
                for item in cart.items.all():
                    # Создаем тикет. Убедитесь, что эти поля есть в tickets/models.py
                    ticket = Ticket.objects.create(
                        client=user,
                        service_name=item.service.name,
                        variant_name=item.variant.name if item.variant else None,
                        price_paid=item.get_price(),
                        user_note=f"Paid Service: {item.service.name}",
                        status='paid' 
                    )
                    tickets_created.append(ticket.ticket_number)

                # Очищаем корзину
                cart.items.all().delete()
                
                # Отправляем письмо
                send_mail(
                    subject="Order Confirmed - DOCUITALY",
                    message=f"Payment received.\nTicket(s) created: {', '.join(tickets_created)}\n\nPlease go to your dashboard and upload the required documents.",
                    from_email=None,
                    recipient_list=[user.email],
                    fail_silently=True
                )
                
            except User.DoesNotExist:
                print("Webhook Error: User not found")
            except Cart.DoesNotExist:
                print("Webhook Error: Cart not found")

    return HttpResponse(status=200)