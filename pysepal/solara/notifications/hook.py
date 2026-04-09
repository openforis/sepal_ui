"""Solara hook: use_notifications()."""

import logging
from typing import Optional, Union

import solara

from .bus import NotificationBus, get_current_bus
from .notifier import NoopNotifier, Notifier

logger = logging.getLogger(__name__)


def use_notifications_from_bus(
    bus: Optional[NotificationBus],
) -> Union[Notifier, NoopNotifier]:
    """Resolve a Notifier from a bus (testable without Solara context)."""
    if bus is None:
        logger.debug(
            "use_notifications() called before NotificationProvider mounted. "
            "Notifications will be silently dropped until next render."
        )
        return NoopNotifier()
    return Notifier(bus)


def use_notifications() -> Union[Notifier, NoopNotifier]:
    """Solara hook: returns a Notifier bound to the current kernel's bus.

    Must be called inside a Solara component function.
    If no NotificationProvider is mounted, returns a NoopNotifier.
    """
    bus = get_current_bus()
    return solara.use_memo(lambda: use_notifications_from_bus(bus), [bus])
