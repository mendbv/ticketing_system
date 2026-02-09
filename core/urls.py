from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
# Импортируем вебхук
from services.webhooks import stripe_webhook 

# URL, которые НЕ требуют перевода (языкового префикса)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    
    # === ВАЖНО: Вебхук должен быть здесь, чтобы не было редиректа 302 ===
    path('services/webhook/stripe/', stripe_webhook, name='stripe_webhook'),
]

# URL, которые требуют перевода (добавляют /en/, /it/)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('tickets/', include('tickets.urls')),
    path('services/', include('services.urls')),
    path('', include('website.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)