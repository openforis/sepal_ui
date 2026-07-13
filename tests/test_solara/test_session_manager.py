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
