"""Tests for @catch_errors notification bus integration."""

import warnings
from unittest.mock import patch

import pytest

from pysepal.scripts.decorator import catch_errors
from pysepal.scripts.warning import SepalWarning
from pysepal.solara.notifications.bus import NotificationBus, _buses
from pysepal.solara.notifications.state import ToastType


class FakeWidget:
    """Minimal stand-in that mimics the old Alert interface for legacy test."""

    def __init__(self):
        """Initialize with empty messages list."""
        self.messages = []

    def reset(self):
        pass

    def add_msg(self, msg, type_="info"):
        self.messages.append((msg, type_))

    def append_msg(self, msg, type_="info"):
        self.messages.append((msg, type_))


class TestCatchErrorsWithBus:
    def setup_method(self):
        _buses.clear()

    def teardown_method(self):
        _buses.clear()

    @patch("pysepal.scripts.decorator._get_notification_bus")
    def test_exception_publishes_error_toast(self, mock_get_bus):
        bus = NotificationBus()
        mock_get_bus.return_value = bus

        class MyClass:
            @catch_errors
            def do_work(self):
                raise ValueError("boom")

        obj = MyClass()
        with pytest.raises(ValueError, match="boom"):
            obj.do_work()

        assert len(bus.toasts.value) == 1
        assert bus.toasts.value[0].type == ToastType.ERROR
        assert bus.toasts.value[0].message == "boom"

    @patch("pysepal.scripts.decorator._get_notification_bus")
    def test_exception_is_reraised(self, mock_get_bus):
        bus = NotificationBus()
        mock_get_bus.return_value = bus

        class MyClass:
            @catch_errors
            def do_work(self):
                raise RuntimeError("fail")

        obj = MyClass()
        with pytest.raises(RuntimeError, match="fail"):
            obj.do_work()

    @patch("pysepal.scripts.decorator._get_notification_bus")
    def test_sepal_warning_publishes_warning_toast(self, mock_get_bus):
        bus = NotificationBus()
        mock_get_bus.return_value = bus

        class MyClass:
            @catch_errors
            def do_work(self):
                warnings.warn(SepalWarning("careful"))
                return "ok"

        obj = MyClass()
        result = obj.do_work()
        assert result == "ok"
        assert len(bus.toasts.value) == 1
        assert bus.toasts.value[0].type == ToastType.WARNING

    @patch("pysepal.scripts.decorator._get_notification_bus")
    def test_return_value_passed_through(self, mock_get_bus):
        mock_get_bus.return_value = NotificationBus()

        class MyClass:
            @catch_errors
            def do_work(self):
                return 42

        assert MyClass().do_work() == 42

    def test_legacy_alert_param_still_works(self):
        """Passing alert= uses old behavior."""
        alert = FakeWidget()

        class MyClass:
            @catch_errors(alert=alert)
            def do_work(self):
                raise ValueError("old style")

        with pytest.raises(ValueError):
            MyClass().do_work()
        assert ("old style", "error") in alert.messages
