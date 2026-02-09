from django.urls import path
from .views import (
    ServiceListView, ServiceDetailView, 
    view_cart, add_to_cart, remove_from_cart, 
    create_checkout_session, payment_success, payment_cancel # Импортируем новые views
)
from .webhooks import stripe_webhook

urlpatterns = [
    path('', ServiceListView.as_view(), name='service_list'),
    
    path('cart/', view_cart, name='view_cart'),
    path('cart/add/<slug:slug>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),

    path('checkout/', create_checkout_session, name='create_checkout_session'),
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/cancel/', payment_cancel, name='payment_cancel'),
    
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook'),

    path('<slug:slug>/', ServiceDetailView.as_view(), name='service_detail'),
]