"""Tests for the admin session panel."""

import solara

from pysepal.solara.components import admin
from pysepal.solara.session_manager import SessionManager


def test_admin_uses_the_canonical_session_helpers():
    """The duplicates in admin.py drifted (no drive/theme flags); they are gone."""
    from pysepal.solara import utils

    assert admin.get_current_session_info is utils.get_current_session_info
    assert admin.get_sessions_overview is utils.get_sessions_overview


def test_admin_button_renders_without_a_session_manager():
    """Voila never runs on_kernel_start, so AdminButton renders manager-less."""
    assert SessionManager.is_initialized() is False

    box, _ = solara.render(admin.AdminButton(), handle_error=False)

    assert box.children[0].children == []


def test_rendering_admin_does_not_initialise_the_session_manager():
    """Building SessionManager() to read info flipped is_initialized() on."""
    solara.render(admin.AdminButton(), handle_error=False)

    assert SessionManager._instance is None
    assert SessionManager.is_initialized() is False
