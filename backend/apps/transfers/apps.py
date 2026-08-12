from django.apps import AppConfig


class TransfersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.transfers"
    label = "transfers"
    verbose_name = "Transfers"

    def ready(self):
        from apps.transfers import tasks as _tasks  # noqa: F401
