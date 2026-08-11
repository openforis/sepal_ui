"""Shared fixtures for the Solara test-suite."""

import pytest

from pysepal.solara import ui_state
from pysepal.solara.session_manager import SessionManager


@pytest.fixture(autouse=True)
def _clean_ui_state():
    """Keep the process-wide UI-state registry from leaking across tests."""
    ui_state._states.clear()
    yield
    ui_state._states.clear()


@pytest.fixture(autouse=True)
def _reset_session_manager():
    """Give every test a pristine SessionManager singleton.

    Plain assignment on purpose: ``monkeypatch.setattr`` would restore the
    stale singleton at teardown and leak it into the rest of the suite.
    """
    SessionManager._instance = None
    SessionManager._sessions = {}
    yield
    SessionManager._instance = None
    SessionManager._sessions = {}
