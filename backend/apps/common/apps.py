from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
    label = "common"
    verbose_name = "Common"

    def ready(self):
        # Ensure shared tasks are registered when Django starts / workers boot.
        from apps.common import tasks as _tasks  # noqa: F401
