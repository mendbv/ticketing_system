from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added, pre_social_login
from allauth.socialaccount.models import SocialAccount
from django.core.files.base import ContentFile
import requests

@receiver(pre_social_login)
def link_google_avatar(sender, request, sociallogin, **kwargs):
    user = sociallogin.user
    
    if not user.avatar:
        if sociallogin.account.provider == 'google':
            data = sociallogin.account.extra_data
            picture_url = data.get('picture')
            
            if picture_url:
                try:
                    response = requests.get(picture_url)
                    if response.status_code == 200:
                        file_name = f"avatar_{user.email.split('@')[0]}.jpg"
                        user.avatar.save(file_name, ContentFile(response.content), save=True)
                except Exception as e:
                    print(f"Error downloading avatar: {e}")