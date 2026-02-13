from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.client_dashboard, name='client_dashboard'),
    path('upload-docs/<int:pk>/', views.client_upload_docs, name='client_upload_docs'),

    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('edit/<int:pk>/', views.edit_ticket, name='edit_ticket'),
    
    path('staff/assign/<int:pk>/', views.staff_assign_ticket, name='staff_assign_ticket'),
]