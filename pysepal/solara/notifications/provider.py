"""NotificationProvider: root component that creates the kernel-scoped bus."""

import logging

import solara

from .bus import NotificationBus, cleanup_bus, create_bus, get_current_bus
from .notification_ui import NotificationUIBridge

logger = logging.getLogger(__name__)


def _get_or_create_current_bus() -> NotificationBus:
    """Return the current bus, creating it immediately when missing.

    Creation happens during render via ``solara.use_memo`` so sibling components
    in the same render pass can resolve a real notifier instead of a transient
    ``NoopNotifier`` on first mount.
    """
    bus = get_current_bus()
    if bus is None:
        bus = create_bus()
        logger.debug("NotificationProvider: created bus")
    return bus


@solara.component
def NotificationProvider():
    """Root notification component. Place once at app top level.

    Creates a kernel-scoped NotificationBus and renders the notification UI.
    Toasts float top-right. Task pill floats bottom-right, tracking the
    MapApp right panel via the published notification offset CSS variable.
    """
    bus = solara.use_memo(_get_or_create_current_bus, [])

    def register_cleanup():
        def on_cleanup():
            cleanup_bus()
            logger.debug("NotificationProvider: cleaned up bus")

        return on_cleanup

    solara.use_effect(register_cleanup, [])

    NotificationUIBridge(bus=bus)
