"""Tests for session locale-state resolution and offered-locale matching."""

import importlib
import inspect
import sys
from types import ModuleType
from unittest.mock import patch

import pysepal
import pysepal.solara.locale as locale_mod
import pysepal.solara.session_manager as sm
from pysepal.solara.locale import (
    LocaleState,
    match_offered_locale,
    resolve_locale_state,
)
from pysepal.solara.session_manager import SessionManager

# --- match_offered_locale: the algorithm every source goes through -----------


def test_match_exact():
    assert match_offered_locale("es-ES", ["en", "es-ES"]) == "es-ES"


def test_match_bare_primary_when_offered():
    assert match_offered_locale("es-419", ["en", "es"]) == "es"


def test_match_falls_back_to_first_offered_variant():
    # es-419 is not offered, bare es is not offered -> first es-* variant wins
    assert match_offered_locale("es-419", ["en", "es-ES", "es-AR"]) == "es-ES"


def test_match_legacy_bare_code_migrates_to_variant():
    # legacy ~/.sepal-ui-config value "es" against a regional-only catalog
    assert match_offered_locale("es", ["en", "es-ES"]) == "es-ES"


def test_match_no_match_and_empty_are_empty():
    assert match_offered_locale("fr", ["en", "es-ES"]) == ""
    assert match_offered_locale("", ["en"]) == ""


# --- LocaleState -------------------------------------------------------------


def test_locale_state_defaults_to_en():
    assert LocaleState().locale == "en"


def test_set_locale_coerces_empty_to_en():
    state = LocaleState("es-ES")
    assert state.locale == "es-ES"
    state.set_locale("")
    assert state.locale == "en"


# --- resolve_locale_state (mirrors test_theme.py) ---------------------------


def test_resolve_returns_explicit_locale_state():
    state = LocaleState("es-ES")
    assert resolve_locale_state(state) is state


def test_resolve_uses_session_locale_state_when_available(monkeypatch):
    session_state = LocaleState("es-ES")
    monkeypatch.setattr(locale_mod, "get_current_locale_state", lambda: session_state)
    assert resolve_locale_state() is session_state


def test_resolve_falls_back_instead_of_raising(monkeypatch):
    def _raise():
        raise RuntimeError("session active but no locale_state")

    monkeypatch.setattr(locale_mod, "get_current_locale_state", _raise)
    result = resolve_locale_state()
    assert isinstance(result, LocaleState)


def test_fallback_is_constant_en_and_never_reads_config(monkeypatch):
    """The process fallback must ignore ~/.sepal-ui-config entirely.

    This is the root fix for app test-suites breaking when a developer's
    config holds a non-English locale (Codex review P0).

    Asserting only ``== "en"`` would be a tautology -- the fallback returns a
    literal. So swap ``pysepal.conf`` for a spy module, reachable through both
    import forms a regression could use (``from pysepal.conf import config_file``
    as ``translator.py`` does, and ``from pysepal import conf`` as
    ``LocaleSelect._read_config_locale`` does), and assert the fallback path
    never touched it.
    """
    touched = []
    real_conf = importlib.import_module("pysepal.conf")

    class _ConfSpy(ModuleType):
        def __getattr__(self, name):
            if not name.startswith("__"):
                touched.append(name)
            return getattr(real_conf, name)

    spy = _ConfSpy("pysepal.conf")
    monkeypatch.setitem(sys.modules, "pysepal.conf", spy)
    monkeypatch.setattr(pysepal, "conf", spy)
    monkeypatch.setattr(locale_mod, "_fallback_locale_state", None)

    def _raise():
        raise RuntimeError("no session")

    monkeypatch.setattr(locale_mod, "get_current_locale_state", _raise)

    assert resolve_locale_state().locale == "en"
    assert touched == []


# --- SessionManager registration --------------------------------------------


def test_get_session_component_returns_locale_state():
    manager = SessionManager()
    state = LocaleState()
    with patch.object(manager, "get_kernel_id", return_value="test-kernel-locale"):
        manager._sessions["test-kernel-locale"] = {"locale_state": state}
        try:
            assert manager.get_session_component("locale_state") is state
        finally:
            del manager._sessions["test-kernel-locale"]


def test_session_creation_source_registers_locale_state():
    """The session-creation code must instantiate LocaleState next to ThemeState.

    Building a real session needs SEPAL headers/GEE credentials, so assert on
    the source: the same guard style upstream uses for import-time contracts.

    Scoped to ``create_session`` (module-wide, ``"locale_state"`` also matches
    ``get_session_info``, so deleting the registration left this green) and
    matched on the whole dict entry rather than the bare key.
    """
    source = inspect.getsource(sm.SessionManager.create_session)
    assert "locale_state = LocaleState()" in source
    assert '"locale_state": locale_state' in source
