"""Tests for session theme-state resolution."""

import pysepal.solara.theme as theme_mod
from pysepal.solara import ui_state
from pysepal.solara.theme import (
    ThemeState,
    get_current_theme_state,
    resolve_theme_state,
)


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


def test_current_theme_state_is_stable_per_scope(monkeypatch):
    """Two reads in the same scope return the same ThemeState instance."""
    monkeypatch.setattr(ui_state, "current_scope_id", lambda: "kernel-a")
    assert get_current_theme_state() is get_current_theme_state()


def test_current_theme_state_is_isolated_per_scope(monkeypatch):
    """Two connections must not share a theme; that was the process-global bug."""
    monkeypatch.setattr(ui_state, "current_scope_id", lambda: "kernel-a")
    first = get_current_theme_state()
    monkeypatch.setattr(ui_state, "current_scope_id", lambda: "kernel-b")
    assert get_current_theme_state() is not first


def test_current_theme_state_never_raises_without_a_session(monkeypatch):
    """A Solara scope with headers but no SEPAL session must still get a theme.

    This used to raise "Session manager is active but no theme state exists".
    Theme is UI state; it has no business failing on an auth condition.
    """
    monkeypatch.setattr(ui_state, "current_scope_id", lambda: "kernel-a")
    assert isinstance(get_current_theme_state(), ThemeState)


def test_current_theme_state_does_not_read_the_legacy_config(monkeypatch):
    """theme.py must not consult ~/.sepal-ui-config (deprecated, issue #977)."""

    def _boom():
        raise AssertionError("get_theme() must not be called from the solara theme path")

    monkeypatch.setattr(theme_mod, "get_theme", _boom, raising=False)
    monkeypatch.setattr(ui_state, "current_scope_id", lambda: "kernel-a")
    assert isinstance(get_current_theme_state(), ThemeState)


def test_theme_module_no_longer_imports_get_theme():
    """The legacy config reader is gone from the solara theme path entirely."""
    assert not hasattr(theme_mod, "get_theme")
