"""Test both LocaleSelect widgets: the legacy v.Menu and the Vue template."""

from pathlib import Path

import pysepal
from pysepal import sepalwidgets as sw
from pysepal.sepalwidgets.vue_app import LocaleSelect
from pysepal.solara.locale import LocaleState
from pysepal.translator import Translator

#: Absolute: tests/test_sepalwidgets/test_App.py chdirs and never restores.
MESSAGE_DIR = Path(pysepal.__file__).parent / "message"

#: pysepal ships a bare ``es`` and an ``ru-RU``; ``locale.parquet`` has neither
#: (only ``es-ES``/``es-AR``/... and ``ru``). Both widgets used to intersect the
#: two sets, so these two languages could never be picked.
BUNDLED = Translator(MESSAGE_DIR)


def test_init() -> None:
    """Check widget init."""
    locale_select = sw.LocaleSelect()

    # minimal btn
    assert isinstance(locale_select, sw.LocaleSelect)
    assert len(locale_select.language_list.children[0].children) == 1

    return


def test_change_language() -> None:
    """Selecting a locale updates the button, and persists nothing."""
    locale_select = sw.LocaleSelect()
    locale_select._on_locale_select({"new": "fr"})
    assert locale_select.btn.children[-1] == "fr"


def test_menu_offers_every_bundled_catalog() -> None:
    locale_select = sw.LocaleSelect(translator=BUNDLED)
    offered = {item.value for item in locale_select.language_list.children[0].children}
    assert offered == set(BUNDLED.available_locales())


def test_menu_value_is_the_locale_code() -> None:
    """A target the parquet lacks used to leave ``value`` an empty DataFrame column."""
    locale_select = sw.LocaleSelect(translator=Translator(MESSAGE_DIR, "es"))
    assert locale_select.value == "es"


def test_vue_offers_every_bundled_catalog() -> None:
    locale_select = LocaleSelect(translator=BUNDLED)
    offered = {record["code"] for record in locale_select.available_locales}
    assert offered == set(BUNDLED.available_locales())


def test_vue_accepts_bare_locale_codes() -> None:
    """MapApp forwards codes rather than a Translator; see test_MapApp."""
    locale_select = LocaleSelect(locales=["en", "es"])
    assert [record["code"] for record in locale_select.available_locales] == ["en", "es"]


def test_vue_borrows_a_display_name_for_a_bare_code() -> None:
    locale_select = LocaleSelect(translator=BUNDLED)
    spanish = next(r for r in locale_select.available_locales if r["code"] == "es")
    assert spanish["name"] == "Spanish"


def test_vue_starts_unbound() -> None:
    assert LocaleSelect().get_locale_state() is None


def test_vue_adopts_the_state_it_is_bound_to() -> None:
    """Binding is the handoff point: the state already holds the resolved code."""
    locale_select = LocaleSelect(translator=BUNDLED, locale_state=LocaleState("fr"))
    assert locale_select.selected_locale == "fr"


def test_a_browser_pick_reaches_the_locale_state() -> None:
    """The frontend assigns ``selected_locale`` directly; nothing else pushes it."""
    state = LocaleState()
    locale_select = LocaleSelect(translator=BUNDLED, locale_state=state)

    locale_select.selected_locale = "es"

    assert state.locale == "es"


def test_a_state_change_reaches_the_widget() -> None:
    state = LocaleState()
    locale_select = LocaleSelect(translator=BUNDLED, locale_state=state)

    state.set_locale("fr")

    assert locale_select.selected_locale == "fr"


def test_rebinding_detaches_the_previous_state() -> None:
    """Otherwise a widget reused across renders drives every state it ever saw."""
    first, second = LocaleState(), LocaleState()
    locale_select = LocaleSelect(locale_state=first)

    locale_select.bind_locale_state(second)
    locale_select.selected_locale = "fr"

    assert second.locale == "fr"
    assert first.locale == "en"


def test_selecting_a_locale_writes_no_config(tmp_path, monkeypatch) -> None:
    """v4 has no ``~/.sepal-ui-config``; the pick lives in the browser."""
    monkeypatch.setenv("HOME", str(tmp_path))
    locale_select = LocaleSelect(translator=BUNDLED, locale_state=LocaleState())

    locale_select.selected_locale = "fr"

    assert list(tmp_path.iterdir()) == []
