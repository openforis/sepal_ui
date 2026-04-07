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


@solara.component
def TaskProgressPill(bus: NotificationBus):
    """Floating pill showing active task count, expandable to detail panel."""
    tasks = bus.tasks.value
    count = active_task_count(tasks)
    expanded, set_expanded = solara.use_state(False)

    # Filter out tasks to display (active + recently finished)
    display_tasks = [
        t
        for t in tasks
        if t.status in ACTIVE_STATUSES or t.status in {TaskStatus.FAILED, TaskStatus.CANCELLED}
    ]

    # Nothing to show
    if not display_tasks and count == 0:
        return

    summary = task_summary_text(count)

    with solara.Div(
        style={
            "position": "fixed",
            "bottom": "16px",
            "left": "16px",
            "z-index": "1000",
            "pointer-events": "auto",
        },
    ):
        if not expanded:
            # Collapsed pill
            rv.Btn(
                rounded=True,
                color="primary",
                dark=True,
                small=True,
                children=[
                    rv.ProgressCircular(
                        indeterminate=True,
                        size=16,
                        width=2,
                        class_="mr-2",
                    )
                    if count > 0
                    else None,
                    summary or f"{len(display_tasks)} task(s)",
                ],
                on_click=lambda *_: set_expanded(True),
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
                            on_click=lambda *_: set_expanded(False),
                        )
                with rv.CardText():
                    if not display_tasks:
                        solara.Text("No active tasks")
                    else:
                        for task in display_tasks:
                            TaskCard(task=task)
