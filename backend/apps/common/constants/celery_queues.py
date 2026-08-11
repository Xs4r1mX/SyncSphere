"""Celery queue name constants.

Phase 4 uses DEFAULT only. Add named queues here later and wire
them via CELERY_TASK_ROUTES without changing task business logic.
"""

CELERY_DEFAULT_QUEUE = "default"
