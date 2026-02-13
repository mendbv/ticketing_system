from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from services.webhooks import stripe_webhook 

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    
    path('services/webhook/stripe/', stripe_webhook, name='stripe_webhook'),
]

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