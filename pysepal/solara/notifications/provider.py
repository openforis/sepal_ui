"""NotificationProvider: root component that creates the kernel-scoped bus."""

import logging

import solara

from .bus import cleanup_bus, create_bus, get_current_bus

logger = logging.getLogger(__name__)


@solara.component
def NotificationProvider(progress_style: str = "pill"):
    """Root notification component. Place once at app top level.

    Creates a kernel-scoped NotificationBus and renders the notification UI
    (ToastStack + TaskProgressPill or TaskProgressStrip).

    Args:
        progress_style: "pill" (default, floating pill) or "strip" (bottom bar, deferred).
    """
    from .task_pill import TaskProgressPill
    from .toast_stack import ToastStack

    # Create bus on first render, cleanup on unmount
    def setup_bus():
        bus = get_current_bus()
        if bus is None:
            bus = create_bus()
            logger.debug("NotificationProvider: created bus")

        def on_cleanup():
            cleanup_bus()
            logger.debug("NotificationProvider: cleaned up bus")

        return on_cleanup

    solara.use_effect(setup_bus, [])

    bus = get_current_bus()
    if bus is None:
        return

    ToastStack(bus=bus)
    if progress_style == "pill":
        TaskProgressPill(bus=bus)
