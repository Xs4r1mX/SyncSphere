from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
    label = "common"
    verbose_name = "Common"

    def ready(self):
        # Ensure shared tasks are registered when Django starts / workers boot.
        import json
        import time

        from apps.common import tasks as _tasks  # noqa: F401

        # #region agent log
        try:
            from core.celery import app as celery_app

            _dbg = {
                "sessionId": "d38c45",
                "runId": "pre-fix",
                "hypothesisId": "B",
                "location": "apps/common/apps.py:ready",
                "message": "CommonConfig.ready imported tasks",
                "data": {
                    "task_exports": list(getattr(_tasks, "__all__", [])),
                    "has_dispatch_attr": hasattr(_tasks, "dispatch_domain_event"),
                    "has_dispatch_registered": (
                        "apps.common.tasks.dispatch_domain_event.dispatch_domain_event"
                        in celery_app.tasks
                    ),
                    "config_class": self.__class__.__name__,
                },
                "timestamp": int(time.time() * 1000),
            }
            with open(
                r"f:\Projects\PERSONAL\SyncSphere\debug-d38c45.log",
                "a",
                encoding="utf-8",
            ) as _f:
                _f.write(json.dumps(_dbg) + "\n")
        except Exception as _exc:
            try:
                with open(
                    r"f:\Projects\PERSONAL\SyncSphere\debug-d38c45.log",
                    "a",
                    encoding="utf-8",
                ) as _f:
                    _f.write(
                        json.dumps(
                            {
                                "sessionId": "d38c45",
                                "runId": "pre-fix",
                                "hypothesisId": "B",
                                "location": "apps/common/apps.py:ready",
                                "message": "CommonConfig.ready log failed",
                                "data": {"error": _exc.__class__.__name__},
                                "timestamp": int(time.time() * 1000),
                            }
                        )
                        + "\n"
                    )
            except Exception:
                pass
        # #endregion
