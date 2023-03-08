"""Test the LocalSelect widget."""

from configparser import ConfigParser

from sepal_ui import sepalwidgets as sw
from sepal_ui.conf import config_file


def test_init() -> None:
    """Check widget init."""
    locale_select = sw.LocaleSelect()

    # minimal btn
    assert isinstance(locale_select, sw.LocaleSelect)
    assert len(locale_select.language_list.children[0].children) == 1

    return


def test_change_language() -> None:
    """Check default language can be change from the widget."""
    locale_select = sw.LocaleSelect()

    # remove any existing config file
    if config_file.is_file():
        config_file.unlink()

    # change value
    locale = "fr"
    locale_select._on_locale_select({"new": locale})
    config = ConfigParser()
    config.read(config_file)
    assert "sepal-ui" in config.sections()
    assert config["sepal-ui"]["locale"] == locale

    return
