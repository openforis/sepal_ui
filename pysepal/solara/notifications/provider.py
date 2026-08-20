"""NotificationProvider: root component that creates the kernel-scoped bus."""

import logging
from typing import Optional

import solara

from pysepal.solara.theme import ThemeState, resolve_theme_state

from .bus import NotificationBus, cleanup_bus, create_bus
from .notification_ui import NotificationUIBridge

logger = logging.getLogger(__name__)


def _get_or_create_current_bus() -> NotificationBus:
    """Return the current bus, creating it when missing, and take a reference.

    Creation happens during render via ``solara.use_memo`` so sibling components
    in the same render pass can resolve a real notifier instead of a transient
    ``NoopNotifier`` on first mount.

    Every mount must go through ``create_bus`` even when a bus already exists:
    each one registers its own ``cleanup_bus`` effect, so a mount that reuses a
    bus without taking a reference lets another mount's unmount tear it down.
    """
    return create_bus()


@solara.component
def NotificationProvider(theme_state: Optional[ThemeState] = None):
    """Root notification component. Place once at app top level.

    Creates a kernel-scoped NotificationBus and renders the notification UI.
    Toasts float top-right. Task pill floats bottom-right, tracking the
    MapApp right panel via the published notification offset CSS variable.

    Args:
        theme_state: Optional explicit theme state. Defaults to the current
            scope's theme state, falling back to a process-wide default if no
            scope can be resolved, so the pill and toasts follow the app's
            light/dark theme.
    """
    bus = solara.use_memo(_get_or_create_current_bus, [])
    resolved_theme = resolve_theme_state(theme_state)

    def register_cleanup():
        def on_cleanup():
            cleanup_bus()
            logger.debug("NotificationProvider: cleaned up bus")

        return on_cleanup

    solara.use_effect(register_cleanup, [])

    NotificationUIBridge(bus=bus, theme_state=resolved_theme)
