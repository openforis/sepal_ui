"""Tests for NotificationProvider helpers."""

from unittest.mock import patch

from pysepal.solara.notifications.provider import _get_or_create_current_bus


def test_reuses_existing_bus():
    bus = object()
    with patch(
        "pysepal.solara.notifications.provider.get_current_bus",
        return_value=bus,
    ), patch("pysepal.solara.notifications.provider.create_bus") as create_bus:
        assert _get_or_create_current_bus() is bus
        create_bus.assert_not_called()


def test_creates_bus_when_missing():
    bus = object()
    with patch("pysepal.solara.notifications.provider.get_current_bus", return_value=None,), patch(
        "pysepal.solara.notifications.provider.create_bus",
        return_value=bus,
    ) as create_bus:
        assert _get_or_create_current_bus() is bus
        create_bus.assert_called_once_with()


def test_provider_helper_creates_bus_with_voila_runtime_id():
    from pysepal.solara.notifications.bus import _bus_refcounts, _buses

    _buses.clear()
    _bus_refcounts.clear()
    try:
        with patch(
            "pysepal.solara.notifications.bus.current_scope_id",
            return_value="voila:provider-kernel",
        ):
            bus = _get_or_create_current_bus()
            assert _get_or_create_current_bus() is bus
    finally:
        _buses.clear()
        _bus_refcounts.clear()
