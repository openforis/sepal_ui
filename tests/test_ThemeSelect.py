from configparser import ConfigParser

import pytest

from sepal_ui import sepalwidgets as sw
from sepal_ui import config_file


class TestThemeSelect:
    def test_init(self, theme_select):

        # minimal btn
        assert isinstance(theme_select, sw.ThemeSelect)

        return

    def test_change_language(self, theme_select):

        # change value
        theme_select.fire_event("click", None)
        config = ConfigParser()
        config.read(config_file)
        assert "sepal-ui" in config.sections()
        assert config["sepal-ui"]["theme"] == "light"

        return

    @pytest.fixture
    def theme_select(self):
        """Create a simple theme_select"""

        # destroy any existing config file
        if config_file.is_file():
            config_file.unlink()

        return sw.ThemeSelect()
