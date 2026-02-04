from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import Category, Service, Cart, CartItem, ServiceVariant

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