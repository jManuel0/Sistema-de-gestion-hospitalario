from django.apps import AppConfig


class MedicosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medicos'
    verbose_name = 'Medicos y citas'

    def ready(self):
        import medicos.signals  # noqa: F401
