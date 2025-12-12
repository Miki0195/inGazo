"""
Celery configuration for InGazo project.
"""

import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('ingazo')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f'Request: {self.request!r}')


# Periodic tasks (Celery Beat)
app.conf.beat_schedule = {
    # Generate rides from recurring templates daily at midnight
    'generate-recurring-rides': {
        'task': 'apps.rides.tasks.generate_recurring_rides',
        'schedule': 60 * 60 * 24,  # Every 24 hours
    },
    # Send ride reminders 1 hour before departure
    'send-ride-reminders': {
        'task': 'apps.notifications.tasks.send_ride_reminders',
        'schedule': 60 * 15,  # Every 15 minutes
    },
    # Clean up expired notifications
    'cleanup-expired-notifications': {
        'task': 'apps.notifications.tasks.cleanup_expired_notifications',
        'schedule': 60 * 60 * 24,  # Every 24 hours
    },
}

