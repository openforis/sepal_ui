"""Test the frontend methods and objects."""

import re
from types import SimpleNamespace

import sepal_ui.scripts.utils as su
from sepal_ui.conf import config
from sepal_ui.frontend.styles import SepalColor


def test_init() -> None:
    """Init a sepalcolor object."""
    sns = SepalColor()
    assert isinstance(sns, SimpleNamespace)

    return


def test_conf() -> None:
    """Check configuration file theme after changing theme."""
    # Specify light theme
    su.set_config("theme", "light")
    dark_theme = False

    # Instantiate
    color = SepalColor()

    # Check that light theme is activated in the object
    assert dark_theme == color._dark_theme

    # change color theme color
    color._dark_theme = True

    # Be sure now dark theme is stored in conf
    assert config.get("sepal-ui", "theme") == "dark"

    return


def test_repr_html() -> None:
    """Check the html representation of a color object."""
    # Arrange
    # select dark theme
    color = SepalColor()
    color._dark_theme = True

    expected_title_dark = "<h3>Current theme: dark</h3>"
    expected_dark = f"primary</br>{color.primary}"

    # read the html result and assert that they look like expected
    html = color._repr_html_().__str__()
    html = re.sub(r"[\n] [ ]+", "", html)
    assert expected_title_dark in html
    assert expected_dark in html

    # select light theme
    color._dark_theme = False

    # same for light theme
    expected_title_light = "<h3>Current theme: light</h3>"
    expected_light = f"primary</br>{color.primary}"

    # read html and assert the values of some produced items
    html = color._repr_html_().__str__()
    html = re.sub(r"[\n] [ ]+", "", html)
    assert expected_title_light in html
    assert expected_light in html

    return
