from django.apps import AppConfig


class RidesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rides'
    verbose_name = 'Rides'

    def ready(self):
        try:
            import apps.rides.signals  # noqa
        except ImportError:
            pass

