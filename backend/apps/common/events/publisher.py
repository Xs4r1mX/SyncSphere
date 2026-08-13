import logging
from typing import Protocol

from apps.common.events.domain_event import DomainEvent

logger = logging.getLogger(__name__)


class _Observer(Protocol):
    def handle(self, event: DomainEvent) -> None: ...


class DomainEventPublisher:
    """
    Sync in-process event bus.

    Observers must fail-open: publisher catches per-observer errors so domain
    operations never fail because of activity/notification side effects.
    """

    def __init__(self) -> None:
        self._observers: list[_Observer] = []

    def subscribe(self, observer: _Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: _Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def clear(self) -> None:
        self._observers.clear()

    def publish(self, event: DomainEvent) -> None:
        for observer in list(self._observers):
            try:
                observer.handle(event)
            except Exception:
                logger.warning(
                    "Domain event observer failed",
                    exc_info=True,
                    extra={
                        "action": event.action,
                        "user_id": event.user_id,
                        "observer": observer.__class__.__name__,
                    },
                )


domain_event_publisher = DomainEventPublisher()
