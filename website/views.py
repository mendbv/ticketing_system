from django.shortcuts import render, get_object_or_404
from .models import News, ContactInfo

def home(request):
    news = News.objects.all().order_by('-created_at')[:6]
    contacts = ContactInfo.objects.first()
    return render(request, 'website/home.html', {'news': news, 'contacts': contacts})

def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    return render(request, 'website/news_detail.html', {'news_item': news_item})