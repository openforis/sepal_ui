"""Tests for notification state model."""


from pysepal.solara.notifications.state import (
    TOAST_TIMEOUT_DEFAULTS,
    TaskStatus,
    Toast,
    ToastType,
    TrackedTask,
)


def test_toast_types():
    assert set(t.value for t in ToastType) == {"success", "info", "warning", "error", "cancel"}


def test_task_statuses():
    assert set(s.value for s in TaskStatus) == {
        "pending",
        "running",
        "completed",
        "failed",
        "cancelled",
    }


def test_toast_timeout_defaults():
    assert TOAST_TIMEOUT_DEFAULTS[ToastType.SUCCESS] == 3.0
    assert TOAST_TIMEOUT_DEFAULTS[ToastType.INFO] == 3.0
    assert TOAST_TIMEOUT_DEFAULTS[ToastType.WARNING] == 3.0
    assert TOAST_TIMEOUT_DEFAULTS[ToastType.ERROR] == 3.0
    assert TOAST_TIMEOUT_DEFAULTS[ToastType.CANCEL] == 3.0


def test_toast_defaults():
    toast = Toast(message="hello")
    assert toast.message == "hello"
    assert toast.type == ToastType.INFO
    assert toast.timeout is None
    assert toast.count == 1
    assert toast.id


def test_toast_effective_timeout_uses_default():
    assert Toast(message="ok", type=ToastType.SUCCESS).effective_timeout() == 3.0


def test_toast_effective_timeout_explicit_overrides():
    assert Toast(message="ok", type=ToastType.SUCCESS, timeout=20.0).effective_timeout() == 20.0


def test_tracked_task_defaults():
    task = TrackedTask(title="Processing")
    assert task.title == "Processing"
    assert task.status == TaskStatus.PENDING
    assert task.milestones == ()
    assert task.progress is None
    assert task.total_steps is None
    assert task.current_step == 0
    assert task.error_message is None
    assert task.completed_at is None
