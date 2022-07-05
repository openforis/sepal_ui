from configparser import ConfigParser

import pytest

from sepal_ui import sepalwidgets as sw
from sepal_ui import config_file


class TestLocalSelect:
    def test_init(self, locale_select):

        # minimal btn
        assert isinstance(locale_select, sw.LocaleSelect)
        assert len(locale_select.language_list.children[0].children) == 1

        return

    def test_change_language(self, locale_select):

        # destroy any existing config file
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

    @pytest.fixture
    def locale_select(self):
        """Create a simple locale_select"""

        return sw.LocaleSelect()
