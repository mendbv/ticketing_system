from django.urls import path
from .views import ServiceListView, ServiceDetailView, view_cart, add_to_cart, remove_from_cart

urlpatterns = [
    path('', ServiceListView.as_view(), name='service_list'),
    
    path('cart/', view_cart, name='view_cart'),
    path('cart/add/<slug:slug>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),

    path('<slug:slug>/', ServiceDetailView.as_view(), name='service_detail'),
]