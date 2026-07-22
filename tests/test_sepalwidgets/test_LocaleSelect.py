"""Test the LocaleSelect widget (browser-owned resolution, no config writes)."""

import pysepal.scripts.utils as su
from pysepal.sepalwidgets.vue_app import LocaleSelect, MapApp
from pysepal.solara.locale import LocaleState
from pysepal.solara.theme import ThemeState

# NOTE: imported directly from `pysepal.sepalwidgets.vue_app` rather than via
# `from pysepal import sepalwidgets as sw`. `pysepal.sepalwidgets.app` defines
# its own pre-existing (upstream, unrelated to this branch) `LocaleSelect`
# (a `v.Menu`-based widget with a `language_list` attribute), and
# `pysepal/sepalwidgets/__init__.py` never imports `vue_app`, so `sw.LocaleSelect`
# resolves to that older class, not this one. Direct-module import is the
# convention this suite already uses for other `vue_app` widgets (see
# `tests/test_sepalwidgets/test_MapApp.py`), and matches how production code
# will consume this widget (`gui/solara_app.py` imports it the same way).


def test_init() -> None:
    locale_select = LocaleSelect()
    assert isinstance(locale_select, LocaleSelect)
    assert locale_select.selected_locale == "en"
    assert locale_select.get_locale_state() is None


def test_config_locale_seeds_from_existing_file(monkeypatch, tmp_path) -> None:
    config = tmp_path / ".sepal-ui-config"
    config.write_text("[sepal-ui]\nlocale = es-ES\n")
    monkeypatch.setattr("pysepal.conf.config_file", config)
    assert LocaleSelect().config_locale == "es-ES"


def test_config_locale_empty_when_no_file(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("pysepal.conf.config_file", tmp_path / "missing")
    assert LocaleSelect().config_locale == ""


def test_selection_updates_state_and_never_writes_config(monkeypatch, tmp_path) -> None:
    # `pysepal.scripts.utils` binds `config`/`config_file` at import time
    # (`from pysepal.conf import config, config_file`) and writes through those
    # module-level names, so monkeypatching `pysepal.conf.config_file` cannot
    # intercept `su.set_config` -- it would happily rewrite the developer's real
    # ~/.sepal-ui-config while the test stayed green. Guard the call itself.
    calls = []
    monkeypatch.setattr(su, "set_config", lambda *args, **kwargs: calls.append(args))
    # secondary guard: nothing may create a config file through pysepal.conf either
    config = tmp_path / ".sepal-ui-config"
    monkeypatch.setattr("pysepal.conf.config_file", config)

    state = LocaleState()
    locale_select = LocaleSelect(locale_state=state)

    locale_select.selected_locale = "fr"

    assert state.locale == "fr"
    assert calls == []
    assert not config.exists()


def test_bind_is_bidirectional() -> None:
    state = LocaleState()
    locale_select = LocaleSelect(locale_state=state)

    state.set_locale("es-ES")
    assert locale_select.selected_locale == "es-ES"

    locale_select.selected_locale = "en"
    assert state.locale == "en"


def test_bind_adopts_state_value() -> None:
    state = LocaleState("es-ES")
    locale_select = LocaleSelect()
    locale_select.bind_locale_state(state)
    assert locale_select.selected_locale == "es-ES"


def test_mapapp_default_selector_is_bound_to_locale_state() -> None:
    """MapApp's implicit LocaleSelect must drive the shared locale state."""
    state = LocaleState("es-ES")
    # theme_state is passed explicitly for the same reason test_MapApp.py does:
    # get_current_theme_state() needs a live Solara kernel context.
    app = MapApp(theme_state=ThemeState(), locale_state=state)
    selector = app.language_selector[0]

    assert selector.get_locale_state() is state
    selector.selected_locale = "fr"
    assert state.locale == "fr"


def test_mapapp_binds_a_supplied_selector() -> None:
    """A caller-supplied selector is bound rather than replaced."""
    state = LocaleState()
    selector = LocaleSelect()
    app = MapApp(theme_state=ThemeState(), locale_state=state, language_selector=[selector])

    assert app.language_selector[0] is selector
    assert selector.get_locale_state() is state
