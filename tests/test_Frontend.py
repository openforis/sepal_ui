import re
from types import SimpleNamespace

import sepal_ui.scripts.utils as su
from sepal_ui import config
from sepal_ui.frontend.styles import SepalColor


class TestFrontend:
    def test_init(self):

        sns = SepalColor()
        assert isinstance(sns, SimpleNamespace)

    def test_conf(self):
        """Check configuration file theme after changing theme"""

        # Specify light theme
        su.set_config("theme", "light")
        dark_theme = False

        # Instantiate
        color = SepalColor()

        # Check that light theme is activated in the object
        assert dark_theme == color._dark_theme

        # act
        # change color theme color

        color._dark_theme = True

        # Be sure now dark theme is stored in conf
        assert config.get("sepal-ui", "theme") == "dark"

    def test_repr_html(self):

        # Arrange
        expected_title_dark = "<h3>Current theme: dark</h3>"
        expected_dark = "primary</br>#b3842e"

        # Act
        color = SepalColor()
        color._dark_theme = True

        html = color._repr_html_().__str__()
        html = re.sub(r"[\n] [ ]+", "", html)

        # Assert
        assert expected_title_dark in html
        assert expected_dark in html

        # Arrange

        expected_title_light = "<h3>Current theme: light</h3>"
        expected_light = "primary</br>#1976D2"

        # Act
        color._dark_theme = False
        html = color._repr_html_().__str__()
        html = re.sub(r"[\n] [ ]+", "", html)

        # Assert
        assert expected_title_light in html
        assert expected_light in html
