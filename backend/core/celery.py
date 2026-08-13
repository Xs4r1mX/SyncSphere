import json
import os
import time

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("syncsphere")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Single default queue now; named queues via CELERY_TASK_ROUTES later.
app.conf.task_default_queue = "default"
app.autodiscover_tasks()

# #region agent log
try:
    _dbg = {
        "sessionId": "d38c45",
        "runId": "pre-fix",
        "hypothesisId": "C",
        "location": "core/celery.py:after_autodiscover",
        "message": "celery tasks after autodiscover",
        "data": {
            "registered": sorted(app.tasks.keys()),
            "has_dispatch": "apps.common.tasks.dispatch_domain_event.dispatch_domain_event"
            in app.tasks,
        },
        "timestamp": int(time.time() * 1000),
    }
    with open(
        r"f:\Projects\PERSONAL\SyncSphere\debug-d38c45.log",
        "a",
        encoding="utf-8",
    ) as _f:
        _f.write(json.dumps(_dbg) + "\n")
except Exception:
    pass
# #endregion
