"""Tests for Notifier (toast publishing) and TaskTracker (context manager)."""

import asyncio

import pytest

from pysepal.solara.notifications.bus import NotificationBus
from pysepal.solara.notifications.notifier import NoopNotifier, Notifier
from pysepal.solara.notifications.state import (
    TaskStatus,
    ToastType,
)


class TestNotifier:
    def setup_method(self):
        self.bus = NotificationBus()
        self.notifier = Notifier(self.bus)

    def test_success(self):
        self.notifier.success("done!")
        assert len(self.bus.toasts.value) == 1
        assert self.bus.toasts.value[0].type == ToastType.SUCCESS
        assert self.bus.toasts.value[0].message == "done!"

    def test_error(self):
        self.notifier.error("failed!")
        assert self.bus.toasts.value[0].type == ToastType.ERROR

    def test_warning(self):
        self.notifier.warning("careful!")
        assert self.bus.toasts.value[0].type == ToastType.WARNING

    def test_info(self):
        self.notifier.info("fyi")
        assert self.bus.toasts.value[0].type == ToastType.INFO

    def test_dismiss(self):
        self.notifier.success("msg")
        toast_id = self.bus.toasts.value[0].id
        self.notifier.dismiss(toast_id)
        assert len(self.bus.toasts.value) == 0


class TestTaskTracker:
    def setup_method(self):
        self.bus = NotificationBus()
        self.notifier = Notifier(self.bus)

    def test_track_creates_task(self):
        with self.notifier.track("Processing"):
            assert len(self.bus.tasks.value) == 1
            assert self.bus.tasks.value[0].status == TaskStatus.RUNNING

    def test_track_auto_completes(self):
        with self.notifier.track("Processing"):
            pass
        assert self.bus.tasks.value[0].status == TaskStatus.COMPLETED

    def test_track_with_total_steps(self):
        with self.notifier.track("Processing", total_steps=3):
            assert self.bus.tasks.value[0].total_steps == 3

    def test_step_adds_milestone(self):
        with self.notifier.track("Processing") as task:
            task.step("Validating...")
        milestones = self.bus.tasks.value[0].milestones
        assert len(milestones) == 1
        assert milestones[0].message == "Validating..."

    def test_step_increments_current_step(self):
        with self.notifier.track("Processing", total_steps=3) as task:
            task.step("Step 1")
            assert self.bus.tasks.value[0].current_step == 1
            task.step("Step 2")
            assert self.bus.tasks.value[0].current_step == 2

    def test_set_progress(self):
        with self.notifier.track("Processing") as task:
            task.set_progress(0.5)
        assert self.bus.tasks.value[0].progress == 0.5

    def test_set_progress_does_not_add_milestone(self):
        with self.notifier.track("Processing") as task:
            task.set_progress(0.5)
        assert len(self.bus.tasks.value[0].milestones) == 0

    def test_update_title(self):
        with self.notifier.track("Processing") as task:
            task.update("New title")
        assert self.bus.tasks.value[0].title == "New title"

    def test_explicit_complete(self):
        with self.notifier.track("Processing") as task:
            task.complete("All done")
        t = self.bus.tasks.value[0]
        assert t.status == TaskStatus.COMPLETED

    def test_explicit_fail(self):
        with self.notifier.track("Processing") as task:
            task.fail("Something broke")
        t = self.bus.tasks.value[0]
        assert t.status == TaskStatus.FAILED
        assert t.error_message == "Something broke"

    def test_explicit_cancel(self):
        with self.notifier.track("Processing") as task:
            task.cancel()
        assert self.bus.tasks.value[0].status == TaskStatus.CANCELLED

    def test_exception_marks_failed_and_publishes_error_toast(self):
        with pytest.raises(ValueError, match="boom"):
            with self.notifier.track("Processing") as task:
                task.step("Step 1")
                raise ValueError("boom")
        t = self.bus.tasks.value[0]
        assert t.status == TaskStatus.FAILED
        assert t.error_message == "boom"
        assert len(t.milestones) == 1  # Step history preserved
        # Error toast published
        assert len(self.bus.toasts.value) == 1
        assert self.bus.toasts.value[0].type == ToastType.ERROR

    def test_cancelled_error_maps_to_cancelled_status(self):
        with pytest.raises(asyncio.CancelledError):
            with self.notifier.track("Processing"):
                raise asyncio.CancelledError()
        assert self.bus.tasks.value[0].status == TaskStatus.CANCELLED
        # No error toast for cancellation
        assert len(self.bus.toasts.value) == 0

    def test_fail_does_not_double_complete(self):
        """If task already failed explicitly, __exit__ should not override."""
        with pytest.raises(RuntimeError):
            with self.notifier.track("Processing") as task:
                task.fail("manual fail")
                raise RuntimeError("also raises")
        assert self.bus.tasks.value[0].status == TaskStatus.FAILED
        assert self.bus.tasks.value[0].error_message == "manual fail"

    def test_exception_after_explicit_complete_overrides_to_failed(self):
        """If user calls complete() then an exception is raised, task becomes FAILED."""
        with pytest.raises(RuntimeError, match="late error"):
            with self.notifier.track("Processing") as task:
                task.complete("All done")
                raise RuntimeError("late error")
        t = self.bus.tasks.value[0]
        assert t.status == TaskStatus.FAILED
        assert t.error_message == "late error"
        # Error toast published
        assert any(
            toast.type == ToastType.ERROR and toast.message == "late error"
            for toast in self.bus.toasts.value
        )

    def test_exception_after_explicit_cancel_does_not_override(self):
        """If user calls cancel() then an exception is raised, task stays CANCELLED."""
        with pytest.raises(RuntimeError):
            with self.notifier.track("Processing") as task:
                task.cancel()
                raise RuntimeError("post-cancel error")
        assert self.bus.tasks.value[0].status == TaskStatus.CANCELLED

    def test_completed_at_set_on_explicit_complete(self):
        """complete() sets the completed_at timestamp."""
        with self.notifier.track("Processing") as task:
            task.complete()
        t = self.bus.tasks.value[0]
        assert t.completed_at is not None
        assert t.completed_at > 0

    def test_completed_at_set_on_auto_complete(self):
        """Auto-complete via __exit__ sets completed_at."""
        with self.notifier.track("Processing"):
            pass
        t = self.bus.tasks.value[0]
        assert t.completed_at is not None
        assert t.completed_at > 0

    def test_completed_at_none_on_failure(self):
        """Failed tasks should not have completed_at set."""
        with pytest.raises(ValueError):
            with self.notifier.track("Processing"):
                raise ValueError("boom")
        t = self.bus.tasks.value[0]
        assert t.status == TaskStatus.FAILED
        assert t.completed_at is None


class TestNoopNotifier:
    def test_noop_toast_methods(self):
        noop = NoopNotifier()
        # Should not raise
        noop.success("msg")
        noop.error("msg")
        noop.warning("msg")
        noop.info("msg")
        noop.dismiss("id")

    def test_noop_track_context_manager(self):
        noop = NoopNotifier()
        with noop.track("Processing") as task:
            task.step("step 1")
            task.set_progress(0.5)
        # Should not raise
