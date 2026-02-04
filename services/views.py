from django.views.generic import ListView, DetailView
from .models import Category, Service

class ServiceListView(ListView):
    model = Category
    template_name = 'services/service_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # Загружаем категории вместе с активными услугами для оптимизации (prefetch)
        return Category.objects.prefetch_related('services').all()

class ServiceDetailView(DetailView):
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'