import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("syncsphere")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Single default queue now; named queues via CELERY_TASK_ROUTES later.
app.conf.task_default_queue = "default"
app.autodiscover_tasks()
