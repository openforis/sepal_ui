"""Tests for the canonical, non-raising session-info helpers.

``AdminButton`` calls these on every render, including under Voila where
``@solara.lab.on_kernel_start`` never fires and no SessionManager exists. They
must report "not ready" rather than raise.
"""

from unittest.mock import patch

from pysepal.solara import utils
from pysepal.solara.runtime_context import UnsupportedSolaraRuntimeError
from pysepal.solara.session_manager import SessionManager


def test_current_session_info_reports_not_ready_without_a_manager():
    assert SessionManager.is_initialized() is False

    info = utils.get_current_session_info()

    assert info["session_ready"] is False
    assert info["username"] is None
    assert info["kernel_id"] is None


def test_current_session_info_does_not_construct_the_manager():
    """Reading info must not flip is_initialized() on as a side effect."""
    assert SessionManager._instance is None

    utils.get_current_session_info()

    assert SessionManager._instance is None
    assert SessionManager.is_initialized() is False


def test_current_session_info_survives_an_unresolvable_runtime():
    manager = SessionManager()
    err = UnsupportedSolaraRuntimeError("no runtime")
    with patch.object(SessionManager, "get_kernel_id", side_effect=err):
        info = utils.get_current_session_info()

    assert info == {
        "kernel_id": None,
        "username": None,
        "has_gee_interface": False,
        "has_sepal_client": False,
        "has_drive_interface": False,
        "has_theme_state": False,
        "active_module_name": None,
        "module_names": [],
        "session_ready": False,
    }
    assert manager is SessionManager()


def test_sessions_overview_is_empty_without_a_manager():
    assert utils.get_sessions_overview() == {
        "total_sessions": 0,
        "ready_sessions": 0,
        "sessions": [],
    }


def test_sessions_overview_counts_ready_sessions():
    manager = SessionManager()
    manager._sessions["kernel-a"] = {"username": "alice", "gee_interface": object()}
    manager._sessions["kernel-b"] = {"username": "bob"}

    overview = utils.get_sessions_overview()

    assert overview["total_sessions"] == 2
    assert overview["ready_sessions"] == 1
    assert {s["username"] for s in overview["sessions"]} == {"alice", "bob"}
