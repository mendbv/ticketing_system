from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from services.models import Cart

class Command(BaseCommand):
    help = 'Deletes carts that have not been updated for more than 7 days'

    def handle(self, *args, **kwargs):
        # Удаляем корзины, которые не обновлялись 7 дней
        cutoff_date = timezone.now() - timedelta(days=7)
        
        # Фильтруем
        old_carts = Cart.objects.filter(updated_at__lt=cutoff_date)
        
        count = old_carts.count()
        
        if count > 0:
            old_carts.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} old carts.'))
        else:
            self.stdout.write(self.style.SUCCESS('No old carts found. System clean.'))