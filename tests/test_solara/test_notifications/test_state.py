"""Tests for notification state model (dataclasses, enums, defaults)."""

from dataclasses import replace

import pytest

from pysepal.solara.notifications.state import (
    TOAST_TIMEOUT_DEFAULTS,
    TaskMilestone,
    TaskStatus,
    Toast,
    ToastType,
    TrackedTask,
)


class TestToastType:
    def test_values(self):
        assert ToastType.SUCCESS.value == "success"
        assert ToastType.INFO.value == "info"
        assert ToastType.WARNING.value == "warning"
        assert ToastType.ERROR.value == "error"


class TestToastTimeoutDefaults:
    def test_success_timeout(self):
        assert TOAST_TIMEOUT_DEFAULTS[ToastType.SUCCESS] == 5.0

    def test_info_timeout(self):
        assert TOAST_TIMEOUT_DEFAULTS[ToastType.INFO] == 5.0

    def test_warning_timeout(self):
        assert TOAST_TIMEOUT_DEFAULTS[ToastType.WARNING] == 10.0

    def test_error_no_timeout(self):
        assert TOAST_TIMEOUT_DEFAULTS[ToastType.ERROR] is None


class TestTaskStatus:
    def test_all_values(self):
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"


class TestToast:
    def test_defaults(self):
        toast = Toast(message="hello")
        assert toast.message == "hello"
        assert toast.type == ToastType.INFO
        assert toast.timeout is None
        assert toast.count == 1
        assert toast.id  # non-empty UUID

    def test_frozen(self):
        toast = Toast(message="hello")
        with pytest.raises(AttributeError):
            toast.message = "world"

    def test_effective_timeout_uses_default(self):
        toast = Toast(message="ok", type=ToastType.SUCCESS)
        assert toast.effective_timeout() == 5.0

    def test_effective_timeout_uses_explicit(self):
        toast = Toast(message="ok", type=ToastType.SUCCESS, timeout=20.0)
        assert toast.effective_timeout() == 20.0

    def test_effective_timeout_error_is_none(self):
        toast = Toast(message="bad", type=ToastType.ERROR)
        assert toast.effective_timeout() is None

    def test_unique_ids(self):
        t1 = Toast(message="a")
        t2 = Toast(message="b")
        assert t1.id != t2.id

    def test_replace_count(self):
        toast = Toast(message="a", count=1)
        updated = replace(toast, count=2)
        assert updated.count == 2
        assert toast.count == 1  # original unchanged


class TestTaskMilestone:
    def test_defaults(self):
        ms = TaskMilestone(message="step 1")
        assert ms.message == "step 1"
        assert ms.timestamp > 0

    def test_frozen(self):
        ms = TaskMilestone(message="step 1")
        with pytest.raises(AttributeError):
            ms.message = "step 2"


class TestTrackedTask:
    def test_defaults(self):
        task = TrackedTask(title="Processing")
        assert task.title == "Processing"
        assert task.status == TaskStatus.PENDING
        assert task.milestones == ()
        assert task.progress is None
        assert task.total_steps is None
        assert task.current_step == 0
        assert task.error_message is None

    def test_frozen(self):
        task = TrackedTask(title="Processing")
        with pytest.raises(AttributeError):
            task.status = TaskStatus.RUNNING

    def test_add_milestone_via_replace(self):
        task = TrackedTask(title="Processing")
        ms = TaskMilestone(message="step 1")
        updated = replace(task, milestones=(*task.milestones, ms), current_step=1)
        assert len(updated.milestones) == 1
        assert updated.current_step == 1
        assert task.milestones == ()  # original unchanged

    def test_update_progress_via_replace(self):
        task = TrackedTask(title="Processing")
        updated = replace(task, progress=0.5)
        assert updated.progress == 0.5
        assert task.progress is None

    def test_unique_ids(self):
        t1 = TrackedTask(title="a")
        t2 = TrackedTask(title="b")
        assert t1.id != t2.id
