from django.apps import AppConfig


class VeterinariaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'veterinaria'

    def ready(self):
        import veterinaria.signals  # noqa