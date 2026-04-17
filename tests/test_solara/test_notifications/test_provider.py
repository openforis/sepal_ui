"""Tests for NotificationProvider helpers."""

from unittest.mock import patch

from pysepal.solara.notifications.provider import _get_or_create_current_bus


class TestNotificationProviderHelpers:
    def test_reuses_existing_bus(self):
        bus = object()
        with patch(
            "pysepal.solara.notifications.provider.get_current_bus",
            return_value=bus,
        ), patch("pysepal.solara.notifications.provider.create_bus") as create_bus:
            assert _get_or_create_current_bus() is bus
            create_bus.assert_not_called()

    def test_creates_bus_when_missing(self):
        bus = object()
        with patch(
            "pysepal.solara.notifications.provider.get_current_bus",
            return_value=None,
        ), patch(
            "pysepal.solara.notifications.provider.create_bus",
            return_value=bus,
        ) as create_bus:
            assert _get_or_create_current_bus() is bus
            create_bus.assert_called_once_with()
