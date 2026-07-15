"""Tests for session theme-state resolution."""

import pysepal.solara.theme as theme_mod
from pysepal.solara.theme import ThemeState, resolve_theme_state


def test_resolve_returns_explicit_theme_state():
    """An explicitly provided theme_state wins over any session lookup."""
    ts = ThemeState(mode="dark")
    assert resolve_theme_state(ts) is ts


def test_resolve_uses_session_theme_state_when_available(monkeypatch):
    """With no explicit state, the current session's theme_state is returned."""
    session_ts = ThemeState(mode="light")
    monkeypatch.setattr(theme_mod, "get_current_theme_state", lambda: session_ts)
    assert resolve_theme_state() is session_ts


def test_resolve_falls_back_instead_of_raising(monkeypatch):
    """A session active but missing its theme component must NOT crash callers.

    ``get_current_theme_state`` raises RuntimeError in that case; ``resolve_*``
    degrades to a real fallback ThemeState so NotificationProvider stays safe.
    """

    def _raise():
        raise RuntimeError("session active but no theme_state")

    monkeypatch.setattr(theme_mod, "get_current_theme_state", _raise)
    result = resolve_theme_state()
    assert isinstance(result, ThemeState)
