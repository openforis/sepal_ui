"""Integration test: full notification flow without Solara server."""

from unittest.mock import patch

import pytest

from pysepal.solara.notifications.bus import (
    _buses,
    create_bus,
)
from pysepal.solara.notifications.notifier import Notifier
from pysepal.solara.notifications.state import (
    TaskStatus,
    ToastType,
)


@pytest.fixture
def clean_buses():
    _buses.clear()
    yield
    _buses.clear()


@patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="test-kernel")
def test_toast_and_task_flow(mock_kid, clean_buses):
    bus = create_bus()
    notifier = Notifier(bus)

    # Publish toasts
    notifier.success("Upload complete")
    notifier.warning("Large file detected")
    notifier.error("Connection timeout")

    assert len(bus.toasts.value) == 3
    assert bus.toasts.value[0].type == ToastType.SUCCESS
    assert bus.toasts.value[1].type == ToastType.WARNING
    assert bus.toasts.value[2].type == ToastType.ERROR

    # Track a task with milestones
    with notifier.track("Processing AOI", total_steps=3) as task:
        task.step("Validating geometry...")
        assert bus.tasks.value[0].current_step == 1
        assert bus.tasks.value[0].status == TaskStatus.RUNNING

        task.step("Fetching from GEE...")
        task.set_progress(0.5)
        assert bus.tasks.value[0].current_step == 2
        assert bus.tasks.value[0].progress == 0.5

        task.step("Clipping raster...")
        task.set_progress(0.9)

    # Task completed
    assert bus.tasks.value[0].status == TaskStatus.COMPLETED
    assert len(bus.tasks.value[0].milestones) == 3

    # Dismiss a toast
    toast_id = bus.toasts.value[0].id
    notifier.dismiss(toast_id)
    assert len(bus.toasts.value) == 2


@patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="test-kernel")
def test_task_failure_flow(mock_kid, clean_buses):
    bus = create_bus()
    notifier = Notifier(bus)

    with pytest.raises(RuntimeError, match="GEE timeout"):
        with notifier.track("Export") as task:
            task.step("Preparing data...")
            task.set_progress(0.3)
            raise RuntimeError("GEE timeout")

    t = bus.tasks.value[0]
    assert t.status == TaskStatus.FAILED
    assert t.error_message == "GEE timeout"
    assert len(t.milestones) == 1
    assert t.milestones[0].message == "Preparing data..."

    # Error toast auto-published
    assert len(bus.toasts.value) == 1
    assert bus.toasts.value[0].type == ToastType.ERROR
    assert "GEE timeout" in bus.toasts.value[0].message


@patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="test-kernel")
def test_concurrent_tasks(mock_kid, clean_buses):
    bus = create_bus()
    notifier = Notifier(bus)

    tracker1 = notifier.track("Task A", total_steps=2)
    tracker2 = notifier.track("Task B")

    with tracker1 as t1:
        t1.step("A step 1")
        with tracker2 as t2:
            t2.step("B step 1")
            t2.set_progress(0.5)
        # tracker2 auto-completed
        t1.step("A step 2")

    assert len(bus.tasks.value) == 2
    assert bus.tasks.value[0].status == TaskStatus.COMPLETED
    assert bus.tasks.value[1].status == TaskStatus.COMPLETED


@patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="test-kernel")
def test_dedup_toasts(mock_kid, clean_buses):
    bus = create_bus()
    notifier = Notifier(bus)

    # Rapid-fire identical toasts
    for _ in range(5):
        notifier.info("Loading...")

    # Should be deduped to one toast with count=5
    assert len(bus.toasts.value) == 1
    assert bus.toasts.value[0].count == 5
