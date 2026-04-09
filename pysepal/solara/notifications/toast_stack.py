"""ToastStack: floating toast notification renderer."""

import time
from typing import Optional

import reacton.ipyvuetify as rv
import solara

from .bus import NotificationBus
from .state import Toast, ToastType

MAX_VISIBLE = 3
ERROR_ROTATION_SECONDS = 30.0

# Color mapping for toast types
TOAST_COLORS = {
    ToastType.SUCCESS: "success",
    ToastType.INFO: "info",
    ToastType.WARNING: "warning",
    ToastType.ERROR: "error",
}


def visible_toasts(
    toasts: list[Toast],
    now: Optional[float] = None,
) -> list[Toast]:
    """Determine which toasts to display (max 3, newest first, error rotation)."""
    if now is None:
        now = time.time()

    # Separate stale errors (older than rotation threshold) from fresh toasts
    stale_errors = []
    fresh = []
    for t in toasts:
        if t.type == ToastType.ERROR and (now - t.created_at) > ERROR_ROTATION_SECONDS:
            stale_errors.append(t)
        else:
            fresh.append(t)

    # Sort fresh by newest first
    fresh.sort(key=lambda t: t.created_at, reverse=True)

    # Take up to MAX_VISIBLE from fresh toasts
    visible = fresh[:MAX_VISIBLE]

    # If there's room and stale errors exist, add them
    remaining_slots = MAX_VISIBLE - len(visible)
    if remaining_slots > 0 and stale_errors:
        stale_errors.sort(key=lambda t: t.created_at, reverse=True)
        visible.extend(stale_errors[:remaining_slots])

    return visible[:MAX_VISIBLE]


@solara.component
def ToastCard(toast: Toast, on_dismiss: callable):
    """A single toast notification card."""
    color = TOAST_COLORS.get(toast.type, "info")
    timeout = toast.effective_timeout()

    count_text = f" (x{toast.count})" if toast.count > 1 else ""

    # Auto-dismiss via use_effect timer (always called — hooks can't be conditional)
    def start_timer():
        if timeout is None:
            return
        import threading

        timer = threading.Timer(timeout, lambda: on_dismiss(toast.id))
        timer.daemon = True
        timer.start()
        return timer.cancel

    solara.use_effect(start_timer, [toast.id])

    with rv.Alert(
        type=color,
        dense=True,
        dismissible=True,
        v_model=True,
        on_v_model=lambda v: on_dismiss(toast.id) if not v else None,
        style_="margin-bottom: 8px; min-width: 300px; opacity: 0.75;",
        elevation=6,
    ):
        solara.Text(f"{toast.message}{count_text}")


@solara.component
def ToastStack(bus: NotificationBus):
    """Renders stacked toast notifications, floating top-right."""
    toasts = bus.toasts.value
    visible = visible_toasts(toasts)

    def dismiss(toast_id):
        bus.remove_toast(toast_id)

    with solara.Column(
        style={
            "position": "fixed",
            "top": "16px",
            "right": "16px",
            "z-index": "1000",
            "width": "350px",
            "pointer-events": "none",
            "display": "flex",
            "flex-direction": "column",
            "gap": "8px",
        },
    ):
        for toast in visible:
            with solara.Div(style={"pointer-events": "auto"}):
                ToastCard(toast=toast, on_dismiss=dismiss)

        # Show rotated error count if any
        stale_error_count = len(toasts) - len(visible)
        if stale_error_count > 0:
            error_count = len([t for t in toasts if t.type == ToastType.ERROR and t not in visible])
            if error_count > 0:
                with solara.Div(style={"pointer-events": "auto"}):
                    rv.Chip(
                        color="error",
                        small=True,
                        children=[f"{error_count} more error(s)"],
                        on_click=lambda *_: None,
                    )
