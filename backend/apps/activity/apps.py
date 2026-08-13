from django.apps import AppConfig


class ActivityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.activity"
    label = "activity"
    verbose_name = "Activity"

    def ready(self) -> None:
        from apps.activity.observers import ActivityLogObserver
        from apps.common.events import domain_event_publisher

        domain_event_publisher.subscribe(ActivityLogObserver())
