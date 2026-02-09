from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import Category, Service, Cart, CartItem, ServiceVariant
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

class ServiceListView(ListView):
    model = Category
    template_name = 'services/service_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.prefetch_related('services').all()

class ServiceDetailView(DetailView):
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'

# === НОВЫЕ ФУНКЦИИ КОРЗИНЫ ===

@login_required
def view_cart(request):
    # Получаем или создаем корзину для пользователя
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'services/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, slug):
    service = get_object_or_404(Service, slug=slug)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    variant_id = request.POST.get('variant')
    variant = None
    
    if variant_id:
        try:
            variant = ServiceVariant.objects.get(id=variant_id)
        except (ServiceVariant.DoesNotExist, ValueError):
            variant = None

    CartItem.objects.create(cart=cart, service=service, variant=variant)
    
    messages.success(request, _("Service added to cart."))
    
    return redirect('service_detail', slug=slug)

@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    messages.info(request, _("Item removed from cart."))
    return redirect('view_cart')

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_checkout_session(request):
    """
    Создает сессию оплаты в Stripe на основе корзины пользователя.
    """
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        return redirect('view_cart')

    line_items = []
    for item in cart.items.all():
        # Формируем название (с вариацией или без)
        product_name = item.service.name
        if item.variant:
            product_name += f" ({item.variant.name})"

        # Stripe принимает цену в копейках/центах (целое число)
        # Наша цена 10.50 евро -> 1050 центов
        price_cents = int(item.get_price() * 100)

        line_items.append({
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': product_name,
                },
                'unit_amount': price_cents,
            },
            'quantity': 1,
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'], # Можно добавить 'paypal', если настроен в Stripe
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri('/services/payment/success/'),
            cancel_url=request.build_absolute_uri('/services/payment/cancel/'),
            metadata={
                'user_id': request.user.id
            }
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        messages.error(request, f"Error connecting to Stripe: {str(e)}")
        return redirect('view_cart')

@login_required
def payment_success(request):
    return render(request, 'services/payment_success.html')

@login_required
def payment_cancel(request):
    return render(request, 'services/payment_cancel.html')