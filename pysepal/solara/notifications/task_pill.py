"""TaskProgressPill: floating task progress indicator with expandable detail."""


import reacton.ipyvuetify as rv
import solara

from .bus import NotificationBus
from .state import TaskMilestone, TaskStatus, TrackedTask

ACTIVE_STATUSES = {TaskStatus.RUNNING, TaskStatus.PENDING}
COMPLETED_FADE_SECONDS = 3.0

# Status colors
STATUS_COLORS = {
    TaskStatus.RUNNING: "primary",
    TaskStatus.PENDING: "grey",
    TaskStatus.COMPLETED: "success",
    TaskStatus.FAILED: "error",
    TaskStatus.CANCELLED: "grey",
}


def active_task_count(tasks: list[TrackedTask]) -> int:
    """Count tasks that are still running or pending."""
    return sum(1 for t in tasks if t.status in ACTIVE_STATUSES)


def task_summary_text(count: int) -> str:
    """Generate summary text for the pill badge."""
    if count == 0:
        return ""
    if count == 1:
        return "1 task running"
    return f"{count} tasks running"


def pill_label(tasks: list[TrackedTask], count: int) -> str:
    """Generate a rich label for the collapsed pill showing latest step."""
    if count == 0:
        # Show last finished task briefly
        finished = [t for t in tasks if t.status in {TaskStatus.COMPLETED, TaskStatus.FAILED}]
        if finished:
            last = finished[-1]
            status = "Done" if last.status == TaskStatus.COMPLETED else "Failed"
            return f"{last.title} — {status}"
        return ""

    # Find the most recent running task
    running = [t for t in tasks if t.status == TaskStatus.RUNNING]
    if not running:
        return task_summary_text(count)

    current = running[-1]
    prefix = current.title
    if current.milestones:
        last_step = current.milestones[-1].message
        label = f"{prefix} — {last_step}"
    else:
        label = f"{prefix}..."

    if count > 1:
        label += f" (+{count - 1} more)"
    return label


@solara.component
def MilestoneTimeline(milestones: tuple[TaskMilestone, ...]):
    """Render a task's milestone history as a timeline."""
    with rv.Timeline(dense=True, align_top=True):
        for ms in milestones:
            with rv.TimelineItem(small=True, color="primary"):
                solara.Text(ms.message)


@solara.component
def TaskCard(task: TrackedTask):
    """A single task entry in the expanded detail panel."""
    color = STATUS_COLORS.get(task.status, "grey")
    expanded, set_expanded = solara.use_state(False)

    with rv.Card(outlined=True, class_="mb-2"):
        with rv.CardTitle(class_="py-2"):
            with solara.Row(justify="space-between", style={"width": "100%"}):
                solara.Text(task.title)
                rv.Chip(
                    x_small=True,
                    color=color,
                    children=[task.status.value],
                )

        # Current step / progress
        with rv.CardText(class_="py-1"):
            if task.milestones:
                last_ms = task.milestones[-1]
                solara.Text(last_ms.message, style={"font-size": "0.85em"})

            if task.progress is not None:
                rv.ProgressLinear(
                    value=int(task.progress * 100),
                    color=color,
                    height=6,
                    rounded=True,
                    class_="mt-1",
                )

            if task.total_steps and task.current_step:
                solara.Text(
                    f"Step {task.current_step}/{task.total_steps}",
                    style={"font-size": "0.75em", "color": "grey"},
                )

            if task.error_message:
                solara.Text(
                    task.error_message,
                    style={"color": "red", "font-size": "0.85em"},
                )

        # Expandable milestone timeline
        if task.milestones:
            with rv.CardActions(class_="py-0"):
                rv.Btn(
                    text=True,
                    x_small=True,
                    children=["Show steps" if not expanded else "Hide steps"],
                    on_click=lambda *_: set_expanded(not expanded),
                )

            if expanded:
                with rv.CardText(class_="pt-0"):
                    MilestoneTimeline(milestones=task.milestones)


_POSITION_PRESETS = {
    "bottom-right": "bottom: 16px; right: 16px;",
    "bottom-left": "bottom: 16px; left: 16px;",
    "map-bottom-right": (
        "bottom: 16px; "
        "right: calc(var(--right-panel-width, 0px) * var(--right-panel-open, 0) + 16px); "
        "transition: right 0.3s ease;"
    ),
}


@solara.component
def TaskProgressPill(bus: NotificationBus, position: str = "bottom-right"):
    """Floating pill showing active task count, expandable to detail panel."""
    tasks = bus.tasks.value
    count = active_task_count(tasks)
    expanded, set_expanded = solara.use_state(False)

    # Stable callbacks (avoid lambda recreation)
    def expand():
        set_expanded(True)

    def collapse():
        set_expanded(False)

    # Filter tasks to display (all non-idle tasks)
    display_tasks = [t for t in tasks if t.status != TaskStatus.PENDING]

    # Auto-remove completed tasks after per-task fade delay
    def cleanup_completed():
        import threading
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

        if any(t.status == TaskStatus.COMPLETED for t in tasks):
            timer = threading.Thread(target=_cleanup, daemon=True)
            timer.start()

    solara.use_effect(
        cleanup_completed, [len([t for t in tasks if t.status == TaskStatus.COMPLETED])]
    )

    has_tasks = len(display_tasks) > 0 or count > 0
    label = pill_label(tasks, count)

    # Resolve position CSS
    pos_css = _POSITION_PRESETS.get(position, position)

    # Always render the container (stable tree), hide via CSS
    with solara.Div(
        style_=(
            f"position: fixed; {pos_css} z-index: 1000; max-width: 500px; "
            f"pointer-events: {'auto' if has_tasks else 'none'}; "
            f"opacity: {'0.92' if has_tasks else '0'}; "
            "transition: opacity 0.3s;"
        ),
    ):
        if not expanded:
            # Collapsed pill with live step info
            children = []
            if count > 0:
                children.append(
                    rv.ProgressCircular(
                        indeterminate=True,
                        size=16,
                        width=2,
                        class_="mr-2",
                    )
                )
            children.append(label or f"{len(display_tasks)} task(s)")

            rv.Btn(
                rounded=True,
                color="primary",
                dark=True,
                small=True,
                children=children,
                on_click=lambda *_: expand(),
                style_="text-transform: none; letter-spacing: normal;",
            )
        else:
            # Expanded detail panel
            with rv.Card(
                max_width=400,
                min_width=300,
                style_="max-height: 400px; overflow-y: auto;",
            ):
                with rv.CardTitle(class_="py-2"):
                    with solara.Row(justify="space-between", style={"width": "100%"}):
                        solara.Text("Task Progress")
                        rv.Btn(
                            icon=True,
                            small=True,
                            children=[rv.Icon(children=["mdi-close"])],
                            on_click=lambda *_: collapse(),
                        )
                with rv.CardText():
                    if not display_tasks:
                        solara.Text("No active tasks")
                    else:
                        for task in display_tasks:
                            TaskCard(task=task)
