from .models import ContactInfo

def global_contacts(request):
    return {'contacts': ContactInfo.objects.first()}