"""Vue-backed notification UI: toasts and task progress pill.

Uses @solara.component_vue to render via Vue template for proper CSS variable
access (--right-panel-width, --right-panel-open from MapApp) and smooth
transitions.
"""

from typing import Callable, Optional

import solara

from .bus import NotificationBus
from .state import TaskStatus, ToastType

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


def _serialize_toasts_from_list(toasts: list) -> list:
    """Serialize a list of Toast objects for Vue template consumption."""
    return [
        {
            "id": t.id,
            "message": t.message,
            "color": _TOAST_COLORS.get(t.type, "info"),
            "created_at": t.created_at,
            "timeout": t.effective_timeout(),
            "count": t.count,
        }
        for t in toasts
    ]


def _serialize_tasks_from_list(tasks: list) -> list:
    """Serialize a list of TrackedTask objects for Vue template consumption."""
    return [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status.value,
            "statusColor": _STATUS_COLORS.get(t.status, "grey"),
            "milestones": [{"message": m.message, "timestamp": m.timestamp} for m in t.milestones],
            "lastStep": t.milestones[-1].message if t.milestones else None,
            "progress": t.progress,
            "totalSteps": t.total_steps,
            "currentStep": t.current_step,
            "errorMessage": t.error_message,
            "createdAt": t.created_at,
            "completedAt": t.completed_at,
        }
        for t in tasks
    ]


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
    """Bridge between the NotificationBus (reactive Python state) and the Vue UI.

    Subscribes to bus.toasts and bus.tasks via Reactive.subscribe() so that
    changes are forwarded to local state without triggering a parent re-render.
    """
    toasts_data, set_toasts_data = solara.use_state([])
    tasks_data, set_tasks_data = solara.use_state([])

    def subscribe_to_bus():
        # Subscribe callbacks fire when .value changes, outside render context.
        def on_toasts_change(new_toasts):
            set_toasts_data(_serialize_toasts_from_list(new_toasts))

        def on_tasks_change(new_tasks):
            set_tasks_data(_serialize_tasks_from_list(new_tasks))

        unsub_toasts = bus.toasts.subscribe(on_toasts_change)
        unsub_tasks = bus.tasks.subscribe(on_tasks_change)

        # Initial sync
        on_toasts_change(bus.toasts.value)
        on_tasks_change(bus.tasks.value)

        def cleanup():
            unsub_toasts()
            unsub_tasks()

        return cleanup

    solara.use_effect(subscribe_to_bus, [])

    def handle_dismiss(toast_id: str):
        bus.remove_toast(toast_id)

    NotificationUI(
        toasts=toasts_data,
        tasks=tasks_data,
        event_dismiss_toast=handle_dismiss,
    )
