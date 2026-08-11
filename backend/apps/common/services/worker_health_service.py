import logging
from typing import Any
from urllib.parse import urlparse

from django.conf import settings

logger = logging.getLogger(__name__)


class WorkerHealthService:
    """Checks Celery broker connectivity and optional worker liveness."""

    @staticmethod
    def check() -> dict[str, Any]:
        broker_ok, broker_error = WorkerHealthService._check_broker()
        workers = WorkerHealthService._inspect_workers() if broker_ok else []

        status = "ok" if broker_ok else "degraded"
        if broker_ok and not workers and not settings.CELERY_TASK_ALWAYS_EAGER:
            # Broker up but no workers reporting — still usable for enqueue.
            status = "degraded"

        return {
            "status": status,
            "broker": {
                "ok": broker_ok,
                "url": WorkerHealthService._safe_broker_url(),
                "error": broker_error,
            },
            "queue": settings.CELERY_TASK_DEFAULT_QUEUE,
            "eager": settings.CELERY_TASK_ALWAYS_EAGER,
            "workers": workers,
            "worker_count": len(workers),
        }

    @staticmethod
    def _safe_broker_url() -> str:
        raw = settings.CELERY_BROKER_URL or ""
        parsed = urlparse(raw)
        host = parsed.hostname or "unknown"
        port = f":{parsed.port}" if parsed.port else ""
        path = parsed.path or ""
        return f"{parsed.scheme}://{host}{port}{path}"

    @staticmethod
    def _check_broker() -> tuple[bool, str | None]:
        try:
            import redis
        except ImportError:
            return False, "redis package is not installed."

        try:
            client = redis.from_url(
                settings.CELERY_BROKER_URL,
                socket_connect_timeout=settings.CELERY_WORKER_HEALTH_TIMEOUT_SECONDS,
                socket_timeout=settings.CELERY_WORKER_HEALTH_TIMEOUT_SECONDS,
            )
            client.ping()
            return True, None
        except Exception as exc:
            logger.warning(
                "Celery broker health check failed",
                extra={"failure_reason": exc.__class__.__name__},
            )
            return False, exc.__class__.__name__

    @staticmethod
    def _inspect_workers() -> list[str]:
        if settings.CELERY_TASK_ALWAYS_EAGER:
            return ["eager"]

        try:
            from core.celery import app as celery_app

            inspector = celery_app.control.inspect(
                timeout=settings.CELERY_WORKER_HEALTH_TIMEOUT_SECONDS
            )
            ping_result = inspector.ping() or {}
            return sorted(ping_result.keys())
        except Exception as exc:
            logger.warning(
                "Celery worker inspect failed",
                extra={"failure_reason": exc.__class__.__name__},
            )
            return []
