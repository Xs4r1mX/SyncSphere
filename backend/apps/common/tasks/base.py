import logging
import time
import uuid
from typing import Any

from celery import Task

logger = logging.getLogger(__name__)

_SENSITIVE_KEYS = {
    "password",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "credentials",
    "authorization",
    "client_secret",
}


class StructuredTask(Task):
    """
    Base Celery task with structured start/finish logging.

    Callers may pass request_id, user_id, operation_id, and provider
    as keyword arguments; they are logged but never treated as secrets.
    """

    abstract = True

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        context = self._extract_context(kwargs)
        started = time.perf_counter()

        logger.info(
            "Celery task started",
            extra={
                **context,
                "task_name": self.name,
                "task_id": self.request.id if self.request else None,
            },
        )

        try:
            result = super().__call__(*args, **kwargs)
        except Exception as exc:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.exception(
                "Celery task failed",
                extra={
                    **context,
                    "task_name": self.name,
                    "task_id": self.request.id if self.request else None,
                    "duration_ms": duration_ms,
                    "failure_reason": exc.__class__.__name__,
                },
            )
            raise

        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info(
            "Celery task completed",
            extra={
                **context,
                "task_name": self.name,
                "task_id": self.request.id if self.request else None,
                "duration_ms": duration_ms,
            },
        )
        return result

    @staticmethod
    def _extract_context(kwargs: dict[str, Any]) -> dict[str, Any]:
        request_id = kwargs.get("request_id") or str(uuid.uuid4())
        return {
            "request_id": request_id,
            "user_id": kwargs.get("user_id"),
            "operation_id": kwargs.get("operation_id"),
            "provider": kwargs.get("provider"),
        }

    @staticmethod
    def scrub_for_logging(payload: dict[str, Any]) -> dict[str, Any]:
        """Return a copy of payload with sensitive keys redacted."""
        scrubbed: dict[str, Any] = {}
        for key, value in payload.items():
            if key.lower() in _SENSITIVE_KEYS:
                scrubbed[key] = "[REDACTED]"
            else:
                scrubbed[key] = value
        return scrubbed
