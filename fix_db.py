import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def fix():
    # 1. Исправляем Site с ID=1
    print("Checking Site configuration...")
    try:
        site = Site.objects.get(pk=1)
        site.domain = 'localhost:8001'
        site.name = 'DOCUITALY'
        site.save()
        print(f"Updated existing Site: {site}")
    except Site.DoesNotExist:
        site = Site.objects.create(pk=1, domain='localhost:8001', name='DOCUITALY')
        print(f"Created new Site: {site}")

    # 2. Создаем заглушку для Google App (чтобы кнопка не вызывала ошибок, если ее нет)
    print("Checking Google SocialApp...")
    if not SocialApp.objects.filter(provider='google').exists():
        app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='placeholder_id',
            secret='placeholder_secret',
        )
        app.sites.add(site)
        print("Created placeholder Google App (Go to Admin to set real keys!)")
    else:
        print("Google App already exists.")

if __name__ == '__main__':
    fix()