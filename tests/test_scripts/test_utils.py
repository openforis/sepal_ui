"""Test the helper methods contained in utils file."""

import random
from configparser import ConfigParser
from unittest.mock import patch

import ee
import geopandas as gpd
import ipyvuetify as v
import pytest
from shapely import geometry as sg

from sepal_ui import sepalwidgets as sw
from sepal_ui.conf import config_file
from sepal_ui.frontend.styles import TYPES
from sepal_ui.scripts import utils as su
from sepal_ui.scripts.warning import SepalWarning


def test_hide_component() -> None:
    """Check we can hide vanilla ipyvuetify widgets."""
    # hide a normal v component
    widget = v.Btn()
    su.hide_component(widget)
    assert "d-none" in widget.class_

    # hide a sepalwidget
    widget = sw.Btn()
    su.hide_component(widget)
    assert widget.viz is False

    return


def test_show_component() -> None:
    """Check we can show vanilla ipyvuetify widgets."""
    # show a normal v component
    widget = v.Btn()
    su.hide_component(widget)
    su.show_component(widget)
    assert "d-none" not in widget.class_

    # show a sepalwidget
    widget = sw.Btn()
    su.hide_component(widget)
    su.show_component(widget)
    assert widget.viz is True

    return


def test_download_link() -> None:
    """Check we can create SEPAL compatible download links."""
    # check the URL for a 'toto/tutu.png' path
    path = "toto/tutu.png"

    expected_link = "https://sepal.io/api/sandbox/jupyter/files/"

    res = su.create_download_link(path)

    assert expected_link in res

    return


def test_random_string() -> None:
    """Check we can create random strings."""
    # use a seed for the random function
    random.seed(1)

    # check default length
    str_ = su.random_string()
    assert len(str_) == 3
    assert str_ == "esz"

    # check parameter length
    str_ = su.random_string(6)
    assert len(str_) == 6
    assert str_ == "ycidpy"

    return


def test_get_file_size() -> None:
    """Check we can display file size in human readable manner."""
    # init test values
    test_value = 7.5
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

    # mock 0 B file
    with patch("pathlib.Path.stat") as stat:
        stat.return_value.st_size = 0

        txt = su.get_file_size("random")
        assert txt == "0.0 B"

    # mock every pow of 1024 to YB
    for i in range(9):
        with patch("pathlib.Path.stat") as stat:
            stat.return_value.st_size = test_value * (1024**i)

            txt = su.get_file_size("random")
            assert txt == f"7.5 {size_name[i]}"

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_init_ee() -> None:
    """Check we can init EE."""
    # check that no error is raised
    su.init_ee()

    return


def test_to_colors() -> None:
    """Check we can handle any color format and transform it back to hex."""
    # setup the same color in several formats
    colors = {
        "hex": "#b8860b",
        "rgb": (0.7215686274509804, 0.5254901960784314, 0.043137254901960784),
        "rgb_int": (184, 134, 11),
        "gee_hex": "b8860b",
        "text": "darkgoldenrod",
    }

    for c in colors.values():
        res = su.to_colors(c)
        assert res == colors["hex"]

    # test that a fake one return black
    res = su.to_colors("toto")
    assert res == "#000000"

    return


def test_next_string() -> None:
    """Check string can be automatically indexed when equals."""
    # Arrange
    input_string = "name"
    output_string = "name_1"

    # Act - assert
    assert su.next_string(input_string) == output_string
    assert su.next_string(input_string)[-1].isdigit()
    assert su.next_string("name_1") == "name_2"

    return


def test_set_config_locale() -> None:
    """Check we can set local config file."""
    # remove any config file that could exist
    if config_file.is_file():
        config_file.unlink()

    # create a config_file with a set language
    locale = "fr-FR"
    su.set_config("locale", locale)

    config = ConfigParser()
    config.read(config_file)
    assert "sepal-ui" in config.sections()
    assert config["sepal-ui"]["locale"] == locale

    # change an existing locale
    locale = "es-CO"
    su.set_config("locale", locale)
    config.read(config_file)
    assert config["sepal-ui"]["locale"] == locale

    # destroy the file again
    config_file.unlink()

    return


def test_set_config_theme() -> None:
    """Check we can set the theme config variable."""
    # remove any config file that could exist
    if config_file.is_file():
        config_file.unlink()

    # create a config_file with a set language
    theme = "dark"
    su.set_config("theme", theme)

    config = ConfigParser()
    config.read(config_file)
    assert "sepal-ui" in config.sections()
    assert config["sepal-ui"]["theme"] == theme

    # change an existing locale
    theme = "light"
    su.set_config("theme", theme)
    config.read(config_file)
    assert config["sepal-ui"]["theme"] == theme

    # destroy the file again
    config_file.unlink()

    return


def test_set_style() -> None:
    """Check we know the authorized type names."""
    # test every legit type
    for t in TYPES:
        assert t == su.set_type(t)

    # test the fallback to info
    with pytest.warns(SepalWarning):
        res = su.set_type("toto")
        assert res == "info"

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_geojson_to_ee() -> None:
    """Check the method to parse geojson into ee.FeatureCollection."""
    # create a point list
    points = [sg.Point(i, i + 1) for i in range(4)]
    d = {"col1": [str(i) for i in range(len(points))], "geometry": points}
    gdf = gpd.GeoDataFrame(d, crs=4326)
    gdf_buffer = gdf.copy().to_crs(3857)
    gdf_buffer.geometry = gdf_buffer.buffer(500)

    # test a featurecollection
    ee_feature_collection = su.geojson_to_ee(gdf_buffer.__geo_interface__)
    assert isinstance(ee_feature_collection, ee.FeatureCollection)
    assert ee_feature_collection.size().getInfo() == len(points)

    # test a feature
    feature = gdf_buffer.iloc[:1].__geo_interface__["features"][0]
    ee_feature = su.geojson_to_ee(feature)
    assert isinstance(ee_feature, ee.Geometry)

    # test a single point
    point = sg.Point(0, 1)
    point = gdf.iloc[:1].__geo_interface__["features"][0]
    ee_point = su.geojson_to_ee(point)
    assert isinstance(ee_point, ee.Geometry)
    assert ee_point.coordinates().getInfo() == [0, 1]

    # test a badly shaped dict
    dict_ = {"type": ""}  # minimal feature from __geo_interface__
    with pytest.raises(ValueError):
        su.geojson_to_ee(dict_)

    return


def test_check_input() -> None:
    """Test if an input is set or not."""
    with pytest.raises(ValueError, match="The value has not been initialized"):
        su.check_input(None)

    with pytest.raises(ValueError, match="toto"):
        su.check_input(None, "toto")

    res = su.check_input(1)
    assert res is True

    # test lists
    res = su.check_input([range(2)])
    assert res is True

    # test empty list
    with pytest.raises(ValueError):
        su.check_input([])

    return
