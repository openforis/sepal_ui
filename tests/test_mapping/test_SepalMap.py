"""Test the SepalMap object."""

import json
import math
import random
from pathlib import Path

import ee
import pytest
from ipyleaflet import GeoJSON

from sepal_ui import mapping as sm
from sepal_ui.frontend import styles as ss
from sepal_ui.frontend.styles import get_theme
from sepal_ui.mapping.legend_control import LegendControl

# create a seed so that we can check values
random.seed(42)


def test_init() -> None:
    """Init a Sepal Map."""
    # check that the map start with no info
    m = sm.SepalMap()
    id1 = m._id  # to check that the next map has another ID

    assert isinstance(m, sm.SepalMap)
    assert m.center == [0, 0]
    assert m.zoom == 2
    assert len(m.layers) == 2

    basemaps = ["CartoDB.DarkMatter", "CartoDB.Positron"]

    # Get current theme
    dark_theme = True if get_theme() == "dark" else False

    # The basemap will change depending on the current theme.
    assert m.layers[0].name == basemaps[not dark_theme]

    # check that the map start with several basemaps

    m = sm.SepalMap(basemaps)
    assert len(m.layers) == 3
    layers_name = [layer.name for layer in m.layers]
    assert all(b in layers_name for b in basemaps)

    # check that the map start with a DC
    m = sm.SepalMap(dc=True)
    assert m._id != id1
    assert m.dc in m.controls

    # check that the map starts with a vinspector
    m = sm.SepalMap(vinspector=True)
    assert m.v_inspector in m.controls

    # check that the map start with a statebar
    m = sm.SepalMap(statebar=True)
    assert m.state in m.controls

    # check that a wrong layer raise an error if it's not part of the leaflet basemap list
    with pytest.raises(Exception):
        m = sm.SepalMap(["TOTO"])

    return


def test_set_center() -> None:
    """Check the center can be updated."""
    m = sm.SepalMap()

    lat = random.randint(-90, 90)
    lng = random.randint(-180, 180)
    zoom = random.randint(0, 22)
    m.set_center(lng, lat, zoom)

    assert m.zoom == zoom
    assert m.center == [lat, lng]

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def zoom_ee_object() -> None:
    """Check we can zoom on a GEE object."""
    # init objects
    m = sm.SepalMap()
    ee_object = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(
        ee.Filter.eq("ADM0_NAME", "France")
    )

    # zoom without zoom out
    m.zoom_ee_object(ee_object.geometry())

    assert m.center == [46.5135930048161, 2.574509802526499]
    assert m.zoom == 5.0

    # zoom with a zoom_out option
    m.zoom_ee_object(ee_object.geometry(), 3)

    assert m.zoom == 4

    return


def test_zoom_bounds() -> None:
    """Check we can zoom on bounds.

    When specified in the same order as in shapely bounds method.
    """
    # init objects
    m = sm.SepalMap()
    bounds = [
        45.73871293893269,  # minx
        4.9050034976367,  # miny
        45.7746437385302,  # maxx
        4.9050034976367,  # maxy
    ]

    # zoom without zoom_out
    m.zoom_bounds(bounds)

    # it works but we cannot test pure JS from here
    # assert m.zoom == 14.0

    # zoom with zoom_out
    m.zoom_bounds(bounds, 5)

    # it works but we cannot test pure JS from here
    # assert m.zoom == 10.0

    return


def test_add_raster(rgb: Path, byte: Path) -> None:
    """Add raster files to the map.

    Args:
        rgb: the path to a rgb image (3 bands)
        byte: the path to a byte image (1 band)
    """
    m = sm.SepalMap()

    # add a rgb layer to the map
    m.add_raster(rgb, layer_name="rgb")
    layer = m.find_layer("rgb")
    assert layer.name == "rgb"
    assert layer.key == "rgb"
    assert type(layer).__name__ == "BoundTileLayer"

    # add a byte layer
    m.add_raster(byte, layer_name="byte")
    layer = m.find_layer("byte")
    assert layer.name == "byte"
    assert layer.key == "byte"

    return


def test_add_colorbar() -> None:
    """Add a colorbar to the map."""
    # create a map and add a colorbar
    m = sm.SepalMap()
    m.add_colorbar(colors=["#fc8d59", "#ffffbf", "#91bfdb"], vmin=0, vmax=5)

    assert len(m.controls) == 5  # only thing I can check

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_add_ee_layer_exceptions() -> None:
    """Check exceptions are raised on ee_layer method."""
    map_ = sm.SepalMap()

    # Test add a non ee map element
    with pytest.raises(AttributeError):
        map_.addLayer({})

    # Test add a feature collection with invalid style
    geometry = ee.FeatureCollection(
        ee.Geometry.Polygon(
            [
                [
                    [-103.198046875, 36.866172202843465],
                    [-103.198046875, 34.655531078083534],
                    [-100.385546875, 34.655531078083534],
                    [-100.385546875, 36.866172202843465],
                ]
            ],
        )
    )

    with pytest.raises(TypeError):
        map_.addLayer(geometry, {"invalid_propery": "red", "fillColor": None})

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_add_ee_layer(image_id: str) -> None:
    """Add a GEE layer on the map.

    Args:
        image_id: the AssetId of the Daniel W. image
    """
    # create map and image
    image = ee.Image(image_id)
    m = sm.SepalMap()

    # display all the viz available in the image
    for viz in sm.SepalMap().get_viz_params(image).values():
        m.addLayer(image, {}, viz["name"], viz_name=viz["name"])

    assert len(m.layers) == 6

    # display an image without properties
    m = sm.SepalMap()

    dataset = ee.Image("CSP/ERGo/1_0/Global/ALOS_mTPI")
    dataset = ee.Image().addBands(dataset)  # with all bands and 0 properties
    m.addLayer(dataset)

    assert len(m.layers) == 3

    # Test with vector

    geometry = ee.FeatureCollection(
        ee.Geometry.Polygon(
            [
                [
                    [-103.198046875, 36.866172202843465],
                    [-103.198046875, 34.655531078083534],
                    [-100.385546875, 34.655531078083534],
                    [-100.385546875, 36.866172202843465],
                ]
            ],
        )
    )

    map_ = sm.SepalMap()
    map_.addLayer(geometry, {"color": "red", "fillColor": None})

    assert len(m.layers) == 3

    return


def test_get_basemap_list() -> None:
    """Set multiple basemaps on the SepalMap."""
    # Retrieve 5 random maps
    random_basemaps = [
        "Esri.OceanBasemap",
        "OpenStreetMap",
        "HikeBike.HikeBike",
        "HikeBike.HillShading",
        "BasemapAT.orthofoto",
    ]

    res = sm.SepalMap.get_basemap_list()

    assert all([bm in res for bm in random_basemaps])

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_get_viz_params(image_id: str) -> None:
    """Check I identify all the viz parameter from Daniel W. asset.

    Args:
        image_id: the AssetId of the GEE image
    """
    image = ee.Image(image_id)
    res = sm.SepalMap().get_viz_params(image)

    expected = {
        "1": {
            "bands": ["ndwi_phase_1", "ndwi_amplitude_1", "ndwi_rmse"],
            "max": [2.40625, 3296.0, 1792.0],
            "name": "NDWI harmonics",
            "min": [-2.1875, 352.0, 320.0],
            "type": "hsv",
            "inverted": [False, False, True],
        },
        "3": {
            "labels": ["Foo", "Bar", "Baz"],
            "bands": ["class"],
            "type": "categorical",
            "name": "Classification",
            "values": [5, 200, 1000],
            "palette": ["#042333", "#b15f82", "#e8fa5b"],
        },
        "2": {
            "bands": ["ndwi"],
            "name": "NDWI",
            "min": -8450,
            "max": 6610,
            "type": "continuous",
            "palette": [
                "#042333",
                "#2c3395",
                "#744992",
                "#b15f82",
                "#eb7958",
                "#fbb43d",
                "#e8fa5b",
            ],
        },
        "0": {
            "max": 2000,
            "type": "rgb",
            "min": 0,
            "name": "RGB",
            "gamma": 1.2,
            "bands": ["red", "green", "blue"],
        },
    }

    assert res == expected

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_remove_layer(ee_map_with_layers: sm.SepalMap) -> None:
    """Remove a specific layer from the map.

    Args:
        ee_map_with_layers: a map supporting multiple ee assets tile layer
    """
    m = ee_map_with_layers

    # remove using a layer without counting the base
    m.remove_layer(0)
    assert len(m.layers) == 5
    assert m.layers[0].base is True

    # remove when authorizing selection of bases
    m.remove_layer(0, base=True)
    assert len(m.layers) == 4
    assert len([ly for ly in m.layers if ly.base is True]) == 0
    # assert m.layers[0].name == "NDWI harmonics"

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_remove_all(ee_map_with_layers: sm.SepalMap) -> None:
    """Remove all layers from the map.

    Args:
        ee_map_with_layers: a map supporting multiple ee assets tile layer
    """
    m = ee_map_with_layers

    m.remove_all()
    assert len(m.layers) == 1

    m.remove_all(base=True)
    assert len(m.layers) == 0

    return


def test_add_layer() -> None:
    """Add geojson layer to the map."""
    m = sm.SepalMap()

    polygon = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-80.37597656249999, 25.720735134412106],
                            [-66.181640625, 18.312810846425442],
                            [-64.8193359375, 32.10118973232094],
                            [-80.37597656249999, 25.720735134412106],
                        ]
                    ],
                },
            }
        ],
    }

    # Arrange without style and requesting default hover.
    geojson = GeoJSON(data=polygon, name="geojson data")

    # Act
    m.add_layer(geojson, hover=True)

    # Assert
    new_layer = m.layers[-1]

    layer_style = json.loads((ss.JSON_DIR / "layer.json").read_text())["layer"]
    hover_style = json.loads((ss.JSON_DIR / "layer_hover.json").read_text())

    assert all([new_layer.style[k] == v for k, v in layer_style.items()])
    assert all([new_layer.hover_style[k] == v for k, v in hover_style.items()])
    assert new_layer.name == "geojson data"
    assert new_layer.key == "geojson_data"

    # Arrange with style
    layer_style = {"color": "blue"}
    layer_hover_style = {"color": "red"}
    geojson = GeoJSON(data=polygon, style=layer_style, hover_style=layer_hover_style)

    # Act
    m.add_layer(geojson)

    # Assert
    new_layer = m.layers[-1]

    assert new_layer.style == layer_style
    assert new_layer.hover_style == layer_hover_style

    return


def test_add_basemap() -> None:
    """Add a basemap to the map."""
    m = sm.SepalMap()
    m.add_basemap("HYBRID")

    assert len(m.layers) == 3
    layer = m.find_layer("Google Satellite", base=True)
    assert layer.name == "Google Satellite"
    assert layer.base is True

    # check that a wrong layer raise an error if it's not part of the leaflet basemap list
    with pytest.raises(Exception):
        m.add_basemap("TOTO")

    return


def test_get_scale():
    """Get the scale of a map."""
    m = sm.SepalMap()
    m.zoom = 5

    assert math.isclose(m.get_scale(), 4891.97)

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_find_layer(ee_map_with_layers: sm.SepalMap) -> None:
    """Find a layer in a map.

    Args:
        ee_map_with_layers: a map supporting multiple ee assets tile layer
    """
    m = ee_map_with_layers

    # search by name
    res = m.find_layer("Classification")
    assert res.name == "Classification"

    # assert the two ways of handling non existing layer
    with pytest.raises(ValueError):
        res = m.find_layer("toto")
    res = m.find_layer("toto", none_ok=True)
    assert res is None

    # search by index
    res = m.find_layer(1)
    assert res.name == "Classification"

    res = m.find_layer(-1)
    assert res.name == "NDWI"

    # out of bounds
    with pytest.raises(ValueError):
        res = m.find_layer(50)

    # search by layer name
    res = m.find_layer(m.layers[3])
    assert res.name == "NDWI harmonics"

    # search by layer key
    res = m.find_layer(m.layers[3].key)
    assert res.name == "NDWI harmonics"

    # search including the basemap
    res = m.find_layer(0, base=True)
    assert "Carto" in res.name
    assert res.base is True

    # search something that is not a key
    with pytest.raises(ValueError):
        m.find_layer(m)

    return


def test_zoom_raster(byte: Path) -> None:
    """Check that we can zoom on a raster.

    Args:
        byte: the path to the image
    """
    m = sm.SepalMap()
    layer = m.add_raster(byte)
    m.zoom_raster(layer)

    center = [33.89703655465772, -117.63458938969723]
    assert all([math.isclose(s, t, rel_tol=0.2) for s, t in zip(m.center, center)])

    # it works but we cannot test pure JS from here
    # assert m.zoom == 15.0

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_add_legend(ee_map_with_layers: sm.SepalMap) -> None:
    """Add a legend to the map.

    Args:
        ee_map_with_layers: a map supporting multiple ee assets tile layer
    """
    legend_dict = {
        "forest": "#b3842e",
        "non forest": "#a1458e",
        "secondary": "#324a88",
        "success": "#3f802a",
        "info": "#79b1c9",
        "warning": "#b8721d",
    }

    ee_map_with_layers.add_legend(legend_dict=legend_dict)

    # just test that is a Legend, the rest is tested by Legend
    assert isinstance(ee_map_with_layers.legend, LegendControl)
    assert ee_map_with_layers.legend.legend_dict == legend_dict

    return


@pytest.fixture(scope="function")
def ee_map_with_layers(image_id: str) -> sm.SepalMap:
    """A sepalMap supporting each combo band from the asset."""
    image = ee.Image(image_id)
    m = sm.SepalMap()

    # display all the viz available in the image
    for viz in sm.SepalMap().get_viz_params(image).values():
        m.addLayer(image, {}, viz["name"], viz_name=viz["name"])

    return m
