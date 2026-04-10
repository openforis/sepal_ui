"""NotificationProvider: root component that creates the kernel-scoped bus."""

import logging

import solara

from .bus import cleanup_bus, create_bus, get_current_bus
from .notification_ui import NotificationUIBridge

logger = logging.getLogger(__name__)


@solara.component
def NotificationProvider():
    """Root notification component. Place once at app top level.

    Creates a kernel-scoped NotificationBus and renders the notification UI.
    Toasts float top-right. Task pill floats bottom-right, tracking the
    MapApp right panel via CSS variables (--right-panel-width, --right-panel-open).
    """
    # bus_ready is not read directly, but set_bus_ready(True) triggers a
    # re-render so get_current_bus() below picks up the newly created bus.
    bus_ready, set_bus_ready = solara.use_state(False)

    def setup_bus():
        bus = get_current_bus()
        if bus is None:
            create_bus()
            logger.debug("NotificationProvider: created bus")
        set_bus_ready(True)

        def on_cleanup():
            cleanup_bus()
            logger.debug("NotificationProvider: cleaned up bus")

        return on_cleanup

    solara.use_effect(setup_bus, [])

    bus = get_current_bus()
    if bus is None:
        return

    NotificationUIBridge(bus=bus)
