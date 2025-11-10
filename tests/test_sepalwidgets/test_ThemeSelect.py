"""Test the ThemeSelect widget."""

from configparser import ConfigParser

import pytest

from sepal_ui import sepalwidgets as sw
from sepal_ui.conf import config_file
from sepal_ui.frontend.styles import get_theme


def test_init(theme_select: sw.ThemeSelect) -> None:
    """Check Init widget.

    Args:
        theme_select: a widget instance removing all existing config
    """
    # minimal btn
    assert isinstance(theme_select, sw.ThemeSelect)

    return


def test_change_theme(theme_select: sw.ThemeSelect) -> None:
    """Check the preferred theme can be changed from the widget.

    Args:
        theme_select: a widget instance removing all existing config
    """
    # Get the current theme
    themes = ["dark", "light"]
    dark_theme = True if get_theme() == "dark" else False

    # change value using toggle_theme method (fire_event doesn't work in test environment)
    theme_select.toggle_theme()

    config = ConfigParser()
    config.read(config_file)
    assert "sepal-ui" in config.sections()

    # New theme has to be the opposite than the initial
    assert config["sepal-ui"]["theme"] == themes[dark_theme]

    return


@pytest.fixture(scope="function")
def theme_select() -> sw.ThemeSelect:
    """Create a simple theme_select and remove existing config.

    Returns:
        the object instance
    """
    # remove any existing config file
    if config_file.is_file():
        config_file.unlink()

    return sw.ThemeSelect()
