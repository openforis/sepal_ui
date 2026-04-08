"""Vue-backed notification UI: toasts and task progress pill.

Uses @solara.component_vue to render via Vue template for proper CSS variable
access (--right-panel-width, --right-panel-open from MapApp) and smooth
transitions.
"""

from typing import Callable, Optional

import solara

from .bus import NotificationBus
from .state import TaskStatus, ToastType
from .task_pill import COMPLETED_FADE_SECONDS

# Color mapping
_TOAST_COLORS = {
    ToastType.SUCCESS: "success",
    ToastType.INFO: "info",
    ToastType.WARNING: "warning",
    ToastType.ERROR: "error",
}

_STATUS_COLORS = {
    TaskStatus.RUNNING: "primary",
    TaskStatus.PENDING: "grey",
    TaskStatus.COMPLETED: "success",
    TaskStatus.FAILED: "error",
    TaskStatus.CANCELLED: "grey",
}


def _serialize_toasts(bus: NotificationBus) -> list:
    """Serialize toasts for Vue template consumption."""
    result = []
    for t in bus.toasts.value:
        result.append(
            {
                "id": t.id,
                "message": t.message,
                "color": _TOAST_COLORS.get(t.type, "info"),
                "created_at": t.created_at,
                "timeout": t.effective_timeout(),
                "count": t.count,
            }
        )
    return result


def _serialize_tasks(bus: NotificationBus) -> list:
    """Serialize tracked tasks for Vue template consumption."""
    result = []
    for t in bus.tasks.value:
        result.append(
            {
                "id": t.id,
                "title": t.title,
                "status": t.status.value,
                "statusColor": _STATUS_COLORS.get(t.status, "grey"),
                "milestones": [{"message": m.message} for m in t.milestones],
                "lastStep": t.milestones[-1].message if t.milestones else None,
                "progress": t.progress,
                "totalSteps": t.total_steps,
                "currentStep": t.current_step,
                "errorMessage": t.error_message,
            }
        )
    return result


@solara.component_vue("NotificationUI.vue")
def NotificationUI(
    toasts: list = [],
    tasks: list = [],
    event_dismiss_toast: Optional[Callable[[str], None]] = None,
):
    """Vue-rendered notification UI with toasts and task progress pill."""
    pass


@solara.component
def NotificationUIBridge(bus: NotificationBus):
    """Bridge between the NotificationBus (reactive Python state) and the Vue UI."""
    toasts = _serialize_toasts(bus)
    tasks = _serialize_tasks(bus)

    def handle_dismiss(toast_id: str):
        bus.remove_toast(toast_id)

    # Auto-remove completed tasks after per-task fade delay
    import threading

    def cleanup_completed():
        import time

        def _cleanup():
            while True:
                time.sleep(1)
                now = time.time()
                for t in bus.tasks.value:
                    if (
                        t.status == TaskStatus.COMPLETED
                        and t.completed_at is not None
                        and now - t.completed_at >= COMPLETED_FADE_SECONDS
                    ):
                        bus.remove_task(t.id)
                # Stop polling once no completed tasks remain
                if not any(t.status == TaskStatus.COMPLETED for t in bus.tasks.value):
                    break

        if any(t.status == TaskStatus.COMPLETED for t in bus.tasks.value):
            timer = threading.Thread(target=_cleanup, daemon=True)
            timer.start()

    solara.use_effect(
        cleanup_completed,
        [len([t for t in bus.tasks.value if t.status == TaskStatus.COMPLETED])],
    )

    NotificationUI(
        toasts=toasts,
        tasks=tasks,
        event_dismiss_toast=handle_dismiss,
    )
