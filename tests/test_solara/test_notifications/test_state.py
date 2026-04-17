"""Tests for notification state model."""


from pysepal.solara.notifications.state import (
    TOAST_TIMEOUT_DEFAULTS,
    TaskStatus,
    Toast,
    ToastType,
    TrackedTask,
)


class TestEnums:
    def test_toast_types(self):
        assert set(t.value for t in ToastType) == {"success", "info", "warning", "error", "cancel"}

    def test_task_statuses(self):
        assert set(s.value for s in TaskStatus) == {
            "pending",
            "running",
            "completed",
            "failed",
            "cancelled",
        }


class TestToastTimeoutDefaults:
    def test_all_defaults(self):
        assert TOAST_TIMEOUT_DEFAULTS[ToastType.SUCCESS] == 3.0
        assert TOAST_TIMEOUT_DEFAULTS[ToastType.INFO] == 3.0
        assert TOAST_TIMEOUT_DEFAULTS[ToastType.WARNING] == 3.0
        assert TOAST_TIMEOUT_DEFAULTS[ToastType.ERROR] == 3.0
        assert TOAST_TIMEOUT_DEFAULTS[ToastType.CANCEL] == 3.0


class TestToast:
    def test_defaults(self):
        toast = Toast(message="hello")
        assert toast.message == "hello"
        assert toast.type == ToastType.INFO
        assert toast.timeout is None
        assert toast.count == 1
        assert toast.id

    def test_effective_timeout_uses_default(self):
        assert Toast(message="ok", type=ToastType.SUCCESS).effective_timeout() == 3.0

    def test_effective_timeout_explicit_overrides(self):
        assert Toast(message="ok", type=ToastType.SUCCESS, timeout=20.0).effective_timeout() == 20.0


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
        assert task.completed_at is None
