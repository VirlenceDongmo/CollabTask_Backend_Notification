
from django.core.management.base import BaseCommand
from notify.consumers import start_task_events_consumer

class Command(BaseCommand):
    help = 'Starts the task events consumer'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting task events consumer...'))
        start_task_events_consumer()