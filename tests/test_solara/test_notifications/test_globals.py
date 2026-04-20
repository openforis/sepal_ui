"""Tests for global notify() and track_task() functions."""

import logging
from unittest.mock import patch

import pytest

from pysepal.solara.notifications.bus import _buses
from pysepal.solara.notifications.state import TaskStatus, ToastType


@pytest.fixture
def clean_buses():
    _buses.clear()
    yield
    _buses.clear()


@patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="k1")
def test_notify_publishes_toast(mock_bus_kid, clean_buses):
    from pysepal.solara.notifications.bus import create_bus
    from pysepal.solara.notifications.globals import notify

    bus = create_bus()
    notify("hello", type_="success")
    assert len(bus.toasts.value) == 1
    assert bus.toasts.value[0].message == "hello"
    assert bus.toasts.value[0].type == ToastType.SUCCESS


@patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="k1")
def test_notify_default_type_is_info(mock_bus_kid, clean_buses):
    from pysepal.solara.notifications.bus import create_bus
    from pysepal.solara.notifications.globals import notify

    create_bus()
    notify("hello")
    assert _buses["k1"].toasts.value[0].type == ToastType.INFO


def test_notify_without_provider_logs_warning(caplog, clean_buses):
    from pysepal.solara.notifications.globals import notify

    with caplog.at_level(logging.WARNING):
        notify("hello", type_="error")
    assert "NotificationProvider" in caplog.text


@patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="k1")
def test_track_task_context_manager(mock_bus_kid, clean_buses):
    from pysepal.solara.notifications.bus import create_bus
    from pysepal.solara.notifications.globals import track_task

    bus = create_bus()
    with track_task("Processing", total_steps=2) as task:
        task.step("Step 1")
        task.set_progress(0.5)
    assert len(bus.tasks.value) == 1
    assert bus.tasks.value[0].status == TaskStatus.COMPLETED


def test_track_task_without_provider_is_noop(clean_buses):
    from pysepal.solara.notifications.globals import track_task

    # Should not raise
    with track_task("Processing") as task:
        task.step("Step 1")
