from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Interaction

class Command(BaseCommand):
    help = 'Purge Interaction records older than 180 days'

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timezone.timedelta(days=180)
        old_interactions = Interaction.objects.filter(created_at__lt=cutoff_date)
        count = old_interactions.count()
        old_interactions.delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully purged {count} interaction(s) older than 180 days."))
