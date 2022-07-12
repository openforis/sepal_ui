from configparser import ConfigParser

import pytest

from sepal_ui import config_file, get_theme
from sepal_ui import sepalwidgets as sw


class TestThemeSelect:
    def test_init(self, theme_select):

        # minimal btn
        assert isinstance(theme_select, sw.ThemeSelect)

        return

    def test_change_theme(self, theme_select):

        # Get the current theme
        themes = ["dark", "light"]
        dark_theme = True if get_theme() == "dark" else False

        # change value
        theme_select.fire_event("click", None)
        config = ConfigParser()
        config.read(config_file)
        assert "sepal-ui" in config.sections()

        # New theme has to be the opposite than the initial
        assert config["sepal-ui"]["theme"] == themes[dark_theme]

        return

    @pytest.fixture
    def theme_select(self):
        """Create a simple theme_select"""

        # destroy any existing config file
        if config_file.is_file():
            config_file.unlink()

        return sw.ThemeSelect()
