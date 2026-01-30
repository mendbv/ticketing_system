from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# Маршрут переключения языка (вне i18n_patterns)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# Локализованные маршруты
# Мы убрали prefix_default_language=False, теперь ВСЕ языки имеют префикс (/en/, /it/, /ru/)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), 
    path('accounts/', include('accounts.urls')),            
    path('tickets/', include('tickets.urls')),
    path('', include('website.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)