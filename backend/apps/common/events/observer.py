from typing import Protocol

from apps.common.events.domain_event import DomainEvent


class EventObserver(Protocol):
    def handle(self, event: DomainEvent) -> None:
        """Handle a published domain event (fail-open at publisher level)."""
        ...
