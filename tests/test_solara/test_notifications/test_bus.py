"""Tests for NotificationBus: mutations, dedup, queue limits, thread safety."""

import threading
import time
from unittest.mock import patch

from pysepal.solara.notifications.bus import (
    DEDUP_WINDOW_SECONDS,
    MAX_TOAST_QUEUE,
    NotificationBus,
    _bus_refcounts,
    _buses,
    cleanup_bus,
    create_bus,
    get_current_bus,
)
from pysepal.solara.notifications.state import (
    TaskMilestone,
    TaskStatus,
    Toast,
    ToastType,
    TrackedTask,
)


class TestNotificationBusToasts:
    def setup_method(self):
        self.bus = NotificationBus()

    def test_add_toast(self):
        toast = Toast(message="hello", type=ToastType.SUCCESS)
        self.bus.add_toast(toast)
        assert len(self.bus.toasts.value) == 1
        assert self.bus.toasts.value[0].message == "hello"

    def test_remove_toast(self):
        toast = Toast(message="hello")
        self.bus.add_toast(toast)
        self.bus.remove_toast(toast.id)
        assert len(self.bus.toasts.value) == 0

    def test_remove_nonexistent_toast_is_noop(self):
        self.bus.remove_toast("nonexistent-id")
        assert len(self.bus.toasts.value) == 0

    def test_dedup_merges_identical_toasts(self):
        now = time.time()
        t1 = Toast(message="dup", type=ToastType.INFO, created_at=now)
        t2 = Toast(message="dup", type=ToastType.INFO, created_at=now + 0.5)
        self.bus.add_toast(t1)
        self.bus.add_toast(t2)
        assert len(self.bus.toasts.value) == 1
        assert self.bus.toasts.value[0].count == 2

    def test_no_dedup_after_window(self):
        now = time.time()
        t1 = Toast(message="dup", type=ToastType.INFO, created_at=now)
        t2 = Toast(
            message="dup",
            type=ToastType.INFO,
            created_at=now + DEDUP_WINDOW_SECONDS + 1,
        )
        self.bus.add_toast(t1)
        self.bus.add_toast(t2)
        assert len(self.bus.toasts.value) == 2

    def test_no_dedup_different_type(self):
        now = time.time()
        t1 = Toast(message="msg", type=ToastType.INFO, created_at=now)
        t2 = Toast(message="msg", type=ToastType.ERROR, created_at=now)
        self.bus.add_toast(t1)
        self.bus.add_toast(t2)
        assert len(self.bus.toasts.value) == 2

    def test_queue_limit_drops_oldest_non_errors(self):
        for i in range(MAX_TOAST_QUEUE + 5):
            self.bus.add_toast(
                Toast(message=f"msg-{i}", type=ToastType.INFO, created_at=time.time() + i)
            )
        assert len(self.bus.toasts.value) <= MAX_TOAST_QUEUE

    def test_new_error_replaces_previous_errors(self):
        # New errors replace all previous errors (only the latest is kept)
        for i in range(5):
            self.bus.add_toast(Toast(message=f"err-{i}", type=ToastType.ERROR))
        errors = [t for t in self.bus.toasts.value if t.type == ToastType.ERROR]
        assert len(errors) == 1
        assert errors[0].message == "err-4"

    def test_error_replacement_preserves_non_errors(self):
        # Adding an error should not touch non-error toasts
        self.bus.add_toast(Toast(message="info", type=ToastType.INFO))
        self.bus.add_toast(Toast(message="warn", type=ToastType.WARNING))
        self.bus.add_toast(Toast(message="err", type=ToastType.ERROR))
        self.bus.add_toast(Toast(message="err2", type=ToastType.ERROR))

        non_errors = [t for t in self.bus.toasts.value if t.type != ToastType.ERROR]
        errors = [t for t in self.bus.toasts.value if t.type == ToastType.ERROR]
        assert len(non_errors) == 2
        assert len(errors) == 1
        assert errors[0].message == "err2"


class TestNotificationBusTasks:
    def setup_method(self):
        self.bus = NotificationBus()

    def test_add_task(self):
        task = TrackedTask(title="Processing")
        self.bus.add_task(task)
        assert len(self.bus.tasks.value) == 1
        assert self.bus.tasks.value[0].title == "Processing"

    def test_update_task(self):
        task = TrackedTask(title="Processing")
        self.bus.add_task(task)
        self.bus.update_task(task.id, status=TaskStatus.RUNNING, progress=0.5)
        updated = self.bus.tasks.value[0]
        assert updated.status == TaskStatus.RUNNING
        assert updated.progress == 0.5

    def test_update_nonexistent_task_is_noop(self):
        self.bus.update_task("nonexistent", status=TaskStatus.RUNNING)
        assert len(self.bus.tasks.value) == 0

    def test_remove_task(self):
        task = TrackedTask(title="Processing")
        self.bus.add_task(task)
        self.bus.remove_task(task.id)
        assert len(self.bus.tasks.value) == 0

    def test_add_milestone_via_update(self):
        task = TrackedTask(title="Processing")
        self.bus.add_task(task)
        ms = TaskMilestone(message="step 1")
        self.bus.update_task(
            task.id,
            milestones=(ms,),
            current_step=1,
            status=TaskStatus.RUNNING,
        )
        updated = self.bus.tasks.value[0]
        assert len(updated.milestones) == 1
        assert updated.milestones[0].message == "step 1"
        assert updated.current_step == 1


class TestNotificationBusThreadSafety:
    def test_concurrent_toast_adds(self):
        bus = NotificationBus()
        errors = []

        def add_toasts(start):
            try:
                for i in range(50):
                    bus.add_toast(
                        Toast(message=f"t-{start}-{i}", created_at=time.time() + start + i)
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=add_toasts, args=(n * 100,)) for n in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        # Should have added toasts without crashing (count capped by MAX_TOAST_QUEUE)
        assert len(bus.toasts.value) <= MAX_TOAST_QUEUE


class TestKernelRegistry:
    def setup_method(self):
        _buses.clear()
        _bus_refcounts.clear()

    def teardown_method(self):
        _buses.clear()
        _bus_refcounts.clear()

    @patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="kernel-1")
    def test_create_and_get_bus(self, mock_kid):
        bus = create_bus()
        assert isinstance(bus, NotificationBus)
        assert get_current_bus() is bus

    @patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="kernel-1")
    def test_cleanup_bus(self, mock_kid):
        create_bus()
        cleanup_bus()
        assert get_current_bus() is None

    @patch("pysepal.solara.notifications.bus._get_kernel_id")
    def test_different_kernels_get_different_buses(self, mock_kid):
        mock_kid.return_value = "kernel-1"
        bus1 = create_bus()
        mock_kid.return_value = "kernel-2"
        bus2 = create_bus()
        assert bus1 is not bus2
        mock_kid.return_value = "kernel-1"
        assert get_current_bus() is bus1

    def test_get_bus_returns_none_without_kernel_context(self):
        # No mock, so _get_kernel_id() will fail
        assert get_current_bus() is None

    @patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="kernel-1")
    def test_create_bus_reuses_existing(self, mock_kid):
        """Double create_bus returns the same bus instance."""
        bus1 = create_bus()
        bus2 = create_bus()
        assert bus1 is bus2

    @patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="kernel-1")
    def test_refcount_prevents_premature_removal(self, mock_kid):
        """cleanup_bus only removes bus when refcount reaches 0."""
        create_bus()
        create_bus()  # refcount = 2
        cleanup_bus()  # refcount = 1
        assert get_current_bus() is not None
        cleanup_bus()  # refcount = 0
        assert get_current_bus() is None

    @patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="kernel-1")
    def test_cleanup_without_create_is_noop(self, mock_kid):
        """cleanup_bus on a non-existent kernel is a safe no-op."""
        cleanup_bus()  # Should not raise
        assert get_current_bus() is None
