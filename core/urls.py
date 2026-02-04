from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    
    # Сначала наши кастомные вьюхи (профиль, стафф панель)
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    
    path('tickets/', include('tickets.urls')),
    path('services/', include('services.urls')),
    path('', include('website.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)