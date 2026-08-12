"""Test the MapApp widget."""

from pathlib import Path

import reacton
import solara

import pysepal
from pysepal import mapping as sm
from pysepal.sepalwidgets.vue_app import LocaleSelect, MapApp, ThemeToggle
from pysepal.solara.locale import LocaleState, get_current_locale_state
from pysepal.solara.theme import ThemeState
from pysepal.translator import Translator

#: Absolute: tests/test_sepalwidgets/test_App.py chdirs and never restores.
MESSAGE_DIR = Path(pysepal.__file__).parent / "message"


def test_mapapp_creates_toggle_bound_to_shared_theme_state() -> None:
    """MapApp should create a toggle that drives the same theme state as the map."""
    theme_state = ThemeState(mode="light", dark=False)
    sepal_map = sm.SepalMap(theme_state=theme_state, gee=False)

    app = MapApp(main_map=[sepal_map], theme_state=theme_state)
    toggle = app.theme_toggle[0]

    assert sepal_map.layers[0].name == "CartoDB.Positron"

    toggle.dark = True
    assert sepal_map.layers[0].name == "CartoDB.DarkMatter"

    toggle.dark = None
    toggle.resolved_dark = False
    assert sepal_map.layers[0].name == "CartoDB.Positron"

    toggle.resolved_dark = True
    assert sepal_map.layers[0].name == "CartoDB.DarkMatter"

    return


def test_theme_toggle_stays_unbound_without_theme_state() -> None:
    """A plain ThemeToggle should keep explicit values until bound explicitly."""
    toggle = ThemeToggle(dark=False)

    assert toggle.get_theme_state() is None
    assert toggle.dark is False

    return


def test_mapapp_creates_a_selector_bound_to_the_shared_locale_state() -> None:
    """Unbound, the selector relabels itself while every string stays English."""
    locale_state = LocaleState()
    app = MapApp(locale_state=locale_state)

    app.language_selector[0].selected_locale = "fr"

    assert locale_state.locale == "fr"


def test_mapapp_falls_back_to_the_scope_locale_state() -> None:
    """Apps that never pass a locale_state still share one per connection."""
    app = MapApp()
    assert app.language_selector[0].get_locale_state() is get_current_locale_state()


def test_mapapp_binds_a_supplied_selector() -> None:
    locale_state = LocaleState()
    selector = LocaleSelect()

    MapApp(language_selector=[selector], locale_state=locale_state)

    assert selector.get_locale_state() is locale_state


def test_mapapp_offers_the_locales_it_is_given() -> None:
    """Without them the default selector can only offer English."""
    translator = Translator(MESSAGE_DIR)
    app = MapApp(locales=translator.available_locales())

    offered = {record["code"] for record in app.language_selector[0].available_locales}

    assert offered == set(translator.available_locales())


def test_mapapp_element_carries_the_locales_through_reacton() -> None:
    """MapApp takes codes, not a Translator, because reacton flattens one.

    ``Translator`` subclasses ``dict``, so reacton hands ``__init__`` a plain
    dict and the widget cannot call ``available_locales()`` on it.
    """
    translator = Translator(MESSAGE_DIR)

    @solara.component
    def Demo():
        MapApp.element(locales=translator.available_locales())

    _, rc = reacton.render(Demo())
    selector = rc.find(MapApp).widget.language_selector[0]

    offered = {record["code"] for record in selector.available_locales}

    assert offered == set(translator.available_locales())
