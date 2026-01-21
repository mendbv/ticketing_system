from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.client_dashboard, name='client_dashboard'),
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('create/', views.create_ticket, name='create_ticket'),
    path('edit/<int:pk>/', views.edit_ticket, name='edit_ticket'),
    path('staff/quick-process/<int:pk>/', views.quick_move_to_processing, name='quick_move_to_processing'),
]