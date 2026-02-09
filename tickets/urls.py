from django.urls import path
from . import views

urlpatterns = [
    # Клиентская часть
    path('dashboard/', views.client_dashboard, name='client_dashboard'),
    path('upload-docs/<int:pk>/', views.client_upload_docs, name='client_upload_docs'),

    # Персонал
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('edit/<int:pk>/', views.edit_ticket, name='edit_ticket'),
    path('staff/quick-process/<int:pk>/', views.quick_move_to_processing, name='quick_move_to_processing'),
]