"""Kernel-scoped notification bus: state management and registry."""

import logging
import threading
from dataclasses import replace
from typing import Dict, Optional

import solara
import solara.server.kernel_context

from .state import Toast, ToastType, TrackedTask

logger = logging.getLogger(__name__)

MAX_TOAST_QUEUE = 20
DEDUP_WINDOW_SECONDS = 2.0


class NotificationBus:
    """Owns notification state for a single kernel/session.

    All mutations produce new list copies (never mutate in place).
    Thread-safe via internal lock.
    """

    def __init__(self):
        """Initialize reactive state containers and thread lock."""
        self.toasts: solara.Reactive[list[Toast]] = solara.reactive([])
        self.tasks: solara.Reactive[list[TrackedTask]] = solara.reactive([])
        self._lock = threading.Lock()

    def add_toast(self, toast: Toast) -> None:
        """Add a toast, applying dedup and queue limit rules."""
        with self._lock:
            current = list(self.toasts.value)

            # Dedup: merge if identical message+type within window
            for i, existing in enumerate(current):
                if (
                    existing.message == toast.message
                    and existing.type == toast.type
                    and (toast.created_at - existing.created_at) < DEDUP_WINDOW_SECONDS
                ):
                    current[i] = replace(existing, count=existing.count + 1)
                    self.toasts.value = current
                    return

            current.append(toast)

            # Enforce queue limit: drop oldest non-errors first
            if len(current) > MAX_TOAST_QUEUE:
                errors = [t for t in current if t.type == ToastType.ERROR]
                non_errors = [t for t in current if t.type != ToastType.ERROR]
                keep_non_errors = max(0, MAX_TOAST_QUEUE - len(errors))
                non_errors = non_errors[-keep_non_errors:] if keep_non_errors else []
                current = errors + non_errors

            self.toasts.value = current

    def remove_toast(self, toast_id: str) -> None:
        """Remove a toast by ID."""
        with self._lock:
            self.toasts.value = [t for t in self.toasts.value if t.id != toast_id]

    def add_task(self, task: TrackedTask) -> None:
        """Add a tracked task."""
        with self._lock:
            self.tasks.value = [*self.tasks.value, task]

    def update_task(self, task_id: str, **changes) -> None:
        """Update a tracked task by ID. Unknown IDs are silently ignored."""
        with self._lock:
            self.tasks.value = [
                replace(t, **changes) if t.id == task_id else t for t in self.tasks.value
            ]

    def remove_task(self, task_id: str) -> None:
        """Remove a tracked task by ID."""
        with self._lock:
            self.tasks.value = [t for t in self.tasks.value if t.id != task_id]


# --- Kernel-scoped bus registry (matches SessionManager pattern) ---

_buses: Dict[str, NotificationBus] = {}
_registry_lock = threading.Lock()


def _get_kernel_id() -> str:
    """Get current Solara kernel ID (same approach as SessionManager)."""
    return str(id(solara.server.kernel_context.get_current_context().kernel))


def get_current_bus() -> Optional[NotificationBus]:
    """Get the NotificationBus for the current kernel, or None."""
    try:
        kernel_id = _get_kernel_id()
    except Exception:
        return None
    with _registry_lock:
        return _buses.get(kernel_id)


def create_bus() -> NotificationBus:
    """Create and register a NotificationBus for the current kernel."""
    kernel_id = _get_kernel_id()
    bus = NotificationBus()
    with _registry_lock:
        _buses[kernel_id] = bus
    logger.debug(f"Created NotificationBus for kernel {kernel_id}")
    return bus


def cleanup_bus() -> None:
    """Remove the NotificationBus for the current kernel."""
    kernel_id = _get_kernel_id()
    with _registry_lock:
        removed = _buses.pop(kernel_id, None)
    if removed:
        logger.debug(f"Cleaned up NotificationBus for kernel {kernel_id}")
