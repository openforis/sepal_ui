"""Tests for Solara SessionManager runtime scoping."""

from unittest.mock import patch

from pysepal.solara.session_manager import SessionManager


def test_session_manager_kernel_id_uses_shared_runtime_resolver():
    manager = SessionManager()

    with patch(
        "pysepal.solara.session_manager.get_current_runtime_id",
        return_value="voila:kernel-1",
    ):
        assert manager.get_kernel_id() == "voila:kernel-1"


def test_getters_fall_back_when_no_session_can_exist():
    """Voila and plain Jupyter have no SEPAL headers, so no session can exist.

    ``setup_sessions`` initialises the SessionManager on every kernel start,
    including under Voila, but ``create_session`` bails out when
    ``headers.value`` is None. Treating "initialised but sessionless" as a
    missing ``@with_sepal_sessions`` therefore broke every non-Solara runtime:
    the headerless fallbacks were unreachable.
    """
    from pysepal.solara import utils

    with (
        patch.object(SessionManager, "is_initialized", return_value=True),
        patch.object(SessionManager, "get_session_component", return_value=None),
        patch.object(utils, "can_create_sessions", return_value=False),
        patch.object(utils, "_get_fallback_gee_interface", return_value="fallback-gee"),
        patch.object(utils, "_get_fallback_drive_interface", return_value="fallback-drive"),
    ):
        assert utils.get_current_gee_interface() == "fallback-gee"
        assert utils.get_current_drive_interface() == "fallback-drive"


def test_getters_still_raise_when_headers_exist_but_session_is_missing():
    """With headers present we ARE in a solara request, so a missing session is a bug.

    That is the case the error message is for -- a Page without
    ``@with_sepal_sessions`` -- and it must keep raising.
    """
    import pytest

    from pysepal.solara import utils

    with (
        patch.object(SessionManager, "is_initialized", return_value=True),
        patch.object(SessionManager, "get_session_component", return_value=None),
        patch.object(utils, "can_create_sessions", return_value=True),
    ):
        # Theme deliberately absent here: it moved to the auth-free scope store
        # (pysepal.solara.ui_state) and is covered by tests/test_solara/test_theme.py.
        for getter in (
            utils.get_current_gee_interface,
            utils.get_current_drive_interface,
        ):
            with pytest.raises(RuntimeError, match="Session manager is active"):
                getter()
