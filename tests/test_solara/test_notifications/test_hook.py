"""Tests for use_notifications hook and bus resolution."""


from pysepal.solara.notifications.bus import (
    NotificationBus,
)
from pysepal.solara.notifications.hook import use_notifications_from_bus
from pysepal.solara.notifications.notifier import NoopNotifier, Notifier
from pysepal.solara.notifications.state import ToastType


def test_use_notifications_from_bus_returns_notifier_with_bus():
    bus = NotificationBus()
    notifier = use_notifications_from_bus(bus)
    assert isinstance(notifier, Notifier)


def test_use_notifications_from_bus_returns_noop_without_bus():
    notifier = use_notifications_from_bus(None)
    assert isinstance(notifier, NoopNotifier)


def test_use_notifications_from_bus_publishes_to_bus():
    bus = NotificationBus()
    notifier = use_notifications_from_bus(bus)
    notifier.success("hello")
    assert len(bus.toasts.value) == 1
    assert bus.toasts.value[0].type == ToastType.SUCCESS
