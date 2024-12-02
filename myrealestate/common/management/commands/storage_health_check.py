from django.core.management.base import BaseCommand
from django.utils import timezone
from ...storage import StorageHealthCheck

class Command(BaseCommand):
    help = 'Check storage system health'

    def handle(self, *args, **kwargs):
        is_healthy, timestamp = StorageHealthCheck.perform_health_check(force_check=True)
        
        self.stdout.write(f"\nStorage Health Check - {timezone.now()}")
        self.stdout.write(f"Status: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")
        self.stdout.write(f"Last Check: {timestamp}")