"""Tests for TaskProgressPill helper logic (non-component, pure Python)."""

from pysepal.solara.notifications.state import (
    TaskMilestone,
    TaskStatus,
    TrackedTask,
)
from pysepal.solara.notifications.task_pill import (
    active_task_count,
    pill_label,
    task_summary_text,
)


class TestActiveTaskCount:
    def test_counts_running_and_pending(self):
        tasks = [
            TrackedTask(title="a", status=TaskStatus.RUNNING),
            TrackedTask(title="b", status=TaskStatus.PENDING),
            TrackedTask(title="c", status=TaskStatus.COMPLETED),
            TrackedTask(title="d", status=TaskStatus.FAILED),
        ]
        assert active_task_count(tasks) == 2

    def test_zero_when_none_active(self):
        tasks = [
            TrackedTask(title="a", status=TaskStatus.COMPLETED),
            TrackedTask(title="b", status=TaskStatus.CANCELLED),
        ]
        assert active_task_count(tasks) == 0

    def test_zero_for_empty_list(self):
        assert active_task_count([]) == 0


class TestTaskSummaryText:
    def test_single_task(self):
        assert task_summary_text(1) == "1 task running"

    def test_multiple_tasks(self):
        assert task_summary_text(3) == "3 tasks running"

    def test_zero_tasks(self):
        assert task_summary_text(0) == ""


class TestPillLabel:
    def test_running_task_with_milestone(self):
        tasks = [
            TrackedTask(
                title="Processing AOI",
                status=TaskStatus.RUNNING,
                milestones=(TaskMilestone(message="Fetching boundaries..."),),
            )
        ]
        assert pill_label(tasks, 1) == "Processing AOI — Fetching boundaries..."

    def test_running_task_no_milestones(self):
        tasks = [TrackedTask(title="Processing AOI", status=TaskStatus.RUNNING)]
        assert pill_label(tasks, 1) == "Processing AOI..."

    def test_multiple_running_tasks(self):
        tasks = [
            TrackedTask(title="Task A", status=TaskStatus.RUNNING),
            TrackedTask(
                title="Task B",
                status=TaskStatus.RUNNING,
                milestones=(TaskMilestone(message="Step 1"),),
            ),
        ]
        result = pill_label(tasks, 2)
        assert "Task B — Step 1" in result
        assert "(+1 more)" in result

    def test_no_active_shows_last_completed(self):
        tasks = [TrackedTask(title="Export", status=TaskStatus.COMPLETED)]
        assert pill_label(tasks, 0) == "Export — Done"

    def test_no_active_shows_last_failed(self):
        tasks = [TrackedTask(title="Export", status=TaskStatus.FAILED)]
        assert pill_label(tasks, 0) == "Export — Failed"

    def test_empty_tasks(self):
        assert pill_label([], 0) == ""
