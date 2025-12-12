from django.apps import AppConfig


class DriversConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.drivers'
    verbose_name = 'Drivers'

    def ready(self):
        try:
            import apps.drivers.signals  # noqa
        except ImportError:
            pass

