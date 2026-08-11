"""Tests for Solara SessionManager runtime scoping."""

from unittest.mock import patch

from pysepal.solara.session_manager import SessionManager


def test_session_manager_scope_id_uses_shared_runtime_resolver():
    manager = SessionManager()

    with patch(
        "pysepal.solara.session_manager.resolve_scope_id",
        return_value="voila:kernel-1",
    ):
        assert manager.get_scope_id() == "voila:kernel-1"


def test_per_connection_getters_raise_when_the_session_is_missing():
    """A Solara-server route without @with_sepal_sessions is a bug, not a fallback.

    The pre-v4 version of this test asked whether headers were present. Header
    presence no longer decides anything: topology does, before any header is
    read.
    """
    import pytest

    from pysepal.solara import session_manager as sm
    from pysepal.solara import utils
    from pysepal.solara._topology import SessionPlan, SessionSource
    from pysepal.solara.errors import SepalSessionError

    plan = SessionPlan(SessionSource.PER_CONNECTION, "test")
    with (
        patch.object(sm, "_current_plan", return_value=plan),
        patch.object(SessionManager, "get_scope_id", return_value="kernel-a"),
    ):
        for getter in (utils.get_current_gee_interface, utils.get_current_drive_interface):
            with pytest.raises(SepalSessionError, match="with_sepal_sessions"):
                getter()


def test_session_dict_no_longer_carries_theme_state():
    """Theme is UI state; it must not live behind an auth-gated session."""
    manager = SessionManager()
    manager._sessions["kernel-a"] = {"username": "alice", "gee_interface": object()}

    info = manager.get_session_info("kernel-a")

    assert "theme_state" not in manager._sessions["kernel-a"]
    assert info["has_theme_state"] is False


def test_session_info_reports_theme_state_from_the_scope_store():
    from pysepal.solara import ui_state
    from pysepal.solara.theme import ThemeState

    manager = SessionManager()
    manager._sessions["kernel-a"] = {"username": "alice", "gee_interface": object()}
    ui_state.get_scoped_state("theme_state", ThemeState, scope_id="kernel-a")

    assert manager.get_session_info("kernel-a")["has_theme_state"] is True


def test_setup_sessions_cleanup_clears_the_scope_ui_state():
    from pysepal.solara import ui_state
    from pysepal.solara.session_manager import setup_sessions
    from pysepal.solara.theme import ThemeState

    with patch("pysepal.solara.session_manager.resolve_scope_id", return_value="kernel-a"):
        cleanup = setup_sessions()
        ui_state.get_scoped_state("theme_state", ThemeState, scope_id="kernel-a")
        cleanup()

    assert ui_state.has_scoped_state("theme_state", "kernel-a") is False
