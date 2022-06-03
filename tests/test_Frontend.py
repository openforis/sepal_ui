import re
from types import SimpleNamespace

from sepal_ui import config
from sepal_ui.frontend.styles import SepalColor
import sepal_ui.scripts.utils as su


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
        expected_html = "<h3>Current theme: light</h3><table><th><svg width='60' height='60'><rect width='60' height='60' style='fill:#0000ff;stroke-width:1;stroke:rgb(255,255,255)'/></svg></th></tr><tr><td>main</br>blue</td></tr></table>"

        # Act
        sns = SepalColor(main="blue")
        sns._dark_theme = False

        html = sns._repr_html_().__str__()
        html = re.sub(r"[\n] [ ]+", "", html)

        # Assert
        assert expected_html == html
