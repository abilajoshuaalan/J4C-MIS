from django.apps import AppConfig


class CasesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cases"
    verbose_name = "J4C Case Management"

    def ready(self):
        from . import signals  # noqa: F401
