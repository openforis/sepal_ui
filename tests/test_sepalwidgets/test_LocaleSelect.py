"""Test the LocalSelect widget."""

from pysepal import sepalwidgets as sw


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
