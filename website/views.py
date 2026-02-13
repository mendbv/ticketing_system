from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import activate
from django.conf import settings
from django.http import HttpResponseRedirect
try:
    from django.utils.http import url_has_allowed_host_and_scheme
except ImportError:
    from django.utils.http import is_safe_url as url_has_allowed_host_and_scheme

from .models import News, ContactInfo

def home(request):
    news = News.objects.all().order_by('-created_at')[:6]
    contacts = ContactInfo.objects.first()
    return render(request, 'website/home.html', {'news': news, 'contacts': contacts})

def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    return render(request, 'website/news_detail.html', {'news_item': news_item})

def switch_language(request):
    if request.method == 'POST':
        lang_code = request.POST.get('language')
        next_url = request.POST.get('next', '/')

        if lang_code and lang_code in [l[0] for l in settings.LANGUAGES]:
            activate(lang_code)
            
            parts = next_url.split('/')
            
            if len(parts) > 1 and parts[1] in [l[0] for l in settings.LANGUAGES]:
                parts[1] = lang_code
                next_url = '/'.join(parts)
            else:
                next_url = f'/{lang_code}{next_url}'

            if not url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
                next_url = f'/{lang_code}/'

            response = HttpResponseRedirect(next_url)
            
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                lang_code,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )
            return response
            
    return redirect('home')