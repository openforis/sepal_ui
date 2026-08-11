"""Construction smoke checks for NotificationProvider in a Voila-like runtime."""

from unittest.mock import patch

import solara

from pysepal.solara.notifications import NotificationProvider
from pysepal.solara.notifications.bus import _bus_refcounts, _buses


@solara.component
def _Page():
    NotificationProvider()


def test_notification_provider_constructs_in_voila_like_runtime():
    _buses.clear()
    _bus_refcounts.clear()
    try:
        with patch(
            "pysepal.solara.notifications.bus.current_scope_id",
            return_value="voila:render-kernel",
        ):
            solara.render(_Page(), handle_error=False)
    finally:
        _buses.clear()
        _bus_refcounts.clear()
