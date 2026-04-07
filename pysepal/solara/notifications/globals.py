"""Global escape-hatch functions: notify() and track_task()."""

import logging
from typing import Optional

from .bus import get_current_bus
from .notifier import Notifier, _NoopTaskTrackerContextManager
from .state import Toast, ToastType

logger = logging.getLogger(__name__)

_TYPE_MAP = {
    "success": ToastType.SUCCESS,
    "info": ToastType.INFO,
    "warning": ToastType.WARNING,
    "error": ToastType.ERROR,
}


def _get_kernel_id() -> Optional[str]:
    """Get kernel ID, returning None if not in Solara context."""
    try:
        import solara.server.kernel_context

        return str(id(solara.server.kernel_context.get_current_context().kernel))
    except Exception:
        return None


def notify(message: str, type: str = "info") -> None:
    """Publish a toast notification from anywhere (non-component code).

    If no NotificationProvider is mounted, logs a warning and drops the message.

    Args:
        message: The notification text.
        type: One of "success", "info", "warning", "error".
    """
    bus = get_current_bus()
    if bus is None:
        logger.warning(
            "notify() called without a mounted NotificationProvider. "
            f"Dropped: {type}={message!r}"
        )
        return

    toast_type = _TYPE_MAP.get(type, ToastType.INFO)
    bus.add_toast(Toast(message=message, type=toast_type))


def track_task(title: str, total_steps: Optional[int] = None):
    """Return a TaskTracker context manager from anywhere (non-component code).

    If no NotificationProvider is mounted, returns a no-op context manager.

    Args:
        title: Task title displayed in the progress panel.
        total_steps: If known, enables "step N/M" display.
    """
    bus = get_current_bus()
    if bus is None:
        logger.warning(
            "track_task() called without a mounted NotificationProvider. " f"Dropped: {title!r}"
        )
        return _NoopTaskTrackerContextManager()

    notifier = Notifier(bus)
    return notifier.track(title, total_steps=total_steps)
