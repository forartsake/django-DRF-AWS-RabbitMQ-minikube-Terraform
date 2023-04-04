from django.apps import AppConfig


class InnotterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'innotter'

    def ready(self):
        from innotter.services.signals import block_user_pages