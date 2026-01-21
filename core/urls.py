from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # Технический URL для смены языка (всегда снаружи i18n_patterns)
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    
    # 1. СТАНДАРТНЫЕ ПУТИ АВТОРИЗАЦИИ (login, logout, password_reset и т.д.)
    # Именно эта строка дает имя 'logout' вашим шаблонам
    path('accounts/', include('django.contrib.auth.urls')),
    
    # 2. ВАШИ ПРИЛОЖЕНИЯ
    path('accounts/', include('accounts.urls')), # Здесь ваш signup
    path('', include('website.urls')),
    path('tickets/', include('tickets.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)