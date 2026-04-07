"""Tests for TaskProgressPill helper logic (non-component, pure Python)."""

from pysepal.solara.notifications.state import (
    TaskStatus,
    TrackedTask,
)
from pysepal.solara.notifications.task_pill import (
    active_task_count,
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
