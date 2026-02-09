from django.urls import path
from .views import StaffUserDetailView, profile_confirmation

urlpatterns = [
    path('staff/user/<int:pk>/', StaffUserDetailView.as_view(), name='staff_user_detail'),
    path('profile/confirm/', profile_confirmation, name='profile_confirmation'),
]