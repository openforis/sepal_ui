"""Tests for the admin session panel."""

import inspect

import solara

from pysepal.solara.components import admin
from pysepal.solara.session_info import SessionInfo
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


def test_admin_reads_session_info_by_attribute():
    """The payload is a frozen dataclass; .get() would raise."""
    source = inspect.getsource(admin._render_session_content)
    assert "session_info.get(" not in source
    assert "has_theme_state" not in source
    assert "session_info.scope_id" in source
    assert "session.has_drive_interface" in source


def test_admin_allowlist_is_configurable(monkeypatch):
    monkeypatch.setenv("PYSEPAL_ADMIN_USERS", "alice, bob")
    assert admin._admin_usernames() == {"alice", "bob"}


def test_admin_allowlist_defaults_to_admin(monkeypatch):
    monkeypatch.delenv("PYSEPAL_ADMIN_USERS", raising=False)
    assert admin._admin_usernames() == {"admin"}


def test_admin_gate_fails_closed_for_a_scope_less_caller(monkeypatch):
    """A caller with no resolvable scope must not see the admin panel.

    ``get_current_session_info()`` reports ``username=None`` for a scope that
    can't be resolved (it never falls back to the process/dev-auth identity's
    username). The gate must treat that ``None`` as "not admin", even under a
    permissive allowlist -- it must never render the panel for it.
    """
    monkeypatch.setenv("PYSEPAL_ADMIN_USERS", "admin")
    monkeypatch.setattr(
        admin,
        "get_current_session_info",
        lambda: SessionInfo(scope_id="process", username=None),
    )

    box, _ = solara.render(admin.AdminButton(), handle_error=False)

    assert box.children[0].children == []
