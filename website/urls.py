from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('switch-language/', views.switch_language, name='switch_language_custom'),
]