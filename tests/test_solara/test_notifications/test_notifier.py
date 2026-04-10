"""Tests for Notifier (toast publishing) and TaskTracker (context manager)."""

import asyncio

import pytest

from pysepal.solara.notifications.bus import NotificationBus
from pysepal.solara.notifications.notifier import Notifier
from pysepal.solara.notifications.state import TaskStatus, ToastType


class TestNotifier:
    def setup_method(self):
        self.bus = NotificationBus()
        self.notifier = Notifier(self.bus)

    @pytest.mark.parametrize(
        "method,expected_type",
        [
            ("success", ToastType.SUCCESS),
            ("error", ToastType.ERROR),
            ("warning", ToastType.WARNING),
            ("info", ToastType.INFO),
        ],
    )
    def test_toast_types(self, method, expected_type):
        getattr(self.notifier, method)("msg")
        assert self.bus.toasts.value[0].type == expected_type

    def test_dismiss(self):
        self.notifier.success("msg")
        self.notifier.dismiss(self.bus.toasts.value[0].id)
        assert len(self.bus.toasts.value) == 0


class TestTaskTracker:
    def setup_method(self):
        self.bus = NotificationBus()
        self.notifier = Notifier(self.bus)

    def test_track_lifecycle(self):
        with self.notifier.track("Processing", total_steps=3) as task:
            assert self.bus.tasks.value[0].status == TaskStatus.RUNNING
            assert self.bus.tasks.value[0].total_steps == 3
            task.step("Step 1")
            task.step("Step 2")
            task.set_progress(0.5)
        t = self.bus.tasks.value[0]
        assert t.status == TaskStatus.COMPLETED
        assert len(t.milestones) == 2
        assert t.current_step == 2
        assert t.progress == 0.5
        assert t.completed_at is not None

    def test_explicit_fail(self):
        with self.notifier.track("Processing") as task:
            task.fail("broke")
        t = self.bus.tasks.value[0]
        assert t.status == TaskStatus.FAILED
        assert t.error_message == "broke"
        assert t.completed_at is not None

    def test_explicit_cancel(self):
        with self.notifier.track("Processing") as task:
            task.cancel()
        assert self.bus.tasks.value[0].status == TaskStatus.CANCELLED
        assert self.bus.tasks.value[0].completed_at is not None

    def test_exception_marks_failed_and_publishes_error_toast(self):
        with pytest.raises(ValueError, match="boom"):
            with self.notifier.track("Processing") as task:
                task.step("Step 1")
                raise ValueError("boom")
        t = self.bus.tasks.value[0]
        assert t.status == TaskStatus.FAILED
        assert t.error_message == "boom"
        assert len(t.milestones) == 1
        assert len(self.bus.toasts.value) == 1
        assert self.bus.toasts.value[0].type == ToastType.ERROR

    def test_cancelled_error_maps_to_cancelled_status(self):
        with pytest.raises(asyncio.CancelledError):
            with self.notifier.track("Processing"):
                raise asyncio.CancelledError()
        assert self.bus.tasks.value[0].status == TaskStatus.CANCELLED
        assert len(self.bus.toasts.value) == 0

    def test_exception_after_explicit_complete_overrides_to_failed(self):
        with pytest.raises(RuntimeError):
            with self.notifier.track("Processing") as task:
                task.complete()
                raise RuntimeError("late error")
        assert self.bus.tasks.value[0].status == TaskStatus.FAILED
