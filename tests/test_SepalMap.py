import json
import math
import random
from pathlib import Path
from urllib.request import urlretrieve

import ee
import pytest
from ipyleaflet import GeoJSON
from sepal_ui import get_theme
from sepal_ui import mapping as sm
from sepal_ui.frontend import styles as ss
from sepal_ui.mapping.legend_control import LegendControl

# create a seed so that we can check values
random.seed(42)

# as using localtileserver is still in beta version it is not yet installed by
# default. Using this lazy import we can skip some tests when in github CD/CI
# will be removed when https://github.com/girder/large_image/pull/927 is ready
try:
    from localtileserver import TileClient  # noqa: F401

    is_set_localtileserver = True
except ModuleNotFoundError:
    is_set_localtileserver = False


class TestSepalMap:
    def test_init(self):

        # check that the map start with no info
        m = sm.SepalMap()
        id1 = m._id  # to check that the next map has another ID

        assert isinstance(m, sm.SepalMap)
        assert m.center == [0, 0]
        assert m.zoom == 2
        assert len(m.layers) == 1

        basemaps = ["CartoDB.DarkMatter", "CartoDB.Positron"]

        # Get current theme
        dark_theme = True if get_theme() == "dark" else False

        # The basemap will change depending on the current theme.
        assert m.layers[0].name == basemaps[not dark_theme]

        # check that the map start with several basemaps

        m = sm.SepalMap(basemaps)
        assert len(m.layers) == 2
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

    def test_set_center(self):

        m = sm.SepalMap()

        lat = random.randint(-90, 90)
        lng = random.randint(-180, 180)
        zoom = random.randint(0, 22)
        m.set_center(lng, lat, zoom)

        assert m.zoom == zoom
        assert m.center == [lat, lng]

        return

    def zoom_ee_object(self):

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

    def test_zoom_bounds(self):

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
        assert m.zoom == 14.0

        # zoom with zoom_out
        m.zoom_bounds(bounds, 5)
        assert m.zoom == 10.0

        return

    @pytest.mark.skipif(
        is_set_localtileserver is False,
        reason="localtileserver implementation is still in beta",
    )
    def test_add_raster(self, rgb, byte):

        m = sm.SepalMap()

        # add a rgb layer to the map
        m.add_raster(rgb, layer_name="rgb")
        assert m.layers[1].name == "rgb"
        assert type(m.layers[1]).__name__ == "BoundTileLayer"

        # add a byte layer
        m.add_raster(byte, layer_name="byte")
        assert m.layers[2].name == "byte"

        return

    def test_add_colorbar(self):

        # create a map and add a colorbar
        m = sm.SepalMap()
        m.add_colorbar(colors=["#fc8d59", "#ffffbf", "#91bfdb"], vmin=0, vmax=5)

        assert len(m.controls) == 5  # only thing I can check

        return

    def test_add_ee_layer_exceptions(self):

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

        with pytest.raises(AttributeError):
            map_.addLayer(geometry, {"invalid_propery": "red", "fillColor": None})

    def test_add_ee_layer(self, asset_image_viz):

        # create map and image
        image = ee.Image(asset_image_viz)
        m = sm.SepalMap()

        # display all the viz available in the image
        for viz in sm.SepalMap.get_viz_params(image).values():
            m.addLayer(image, {}, viz["name"], viz_name=viz["name"])

        assert len(m.layers) == 5

        # display an image without properties
        m = sm.SepalMap()

        dataset = ee.Image("CSP/ERGo/1_0/Global/ALOS_mTPI")
        dataset = ee.Image().addBands(dataset)  # with all bands and 0 properties
        m.addLayer(dataset)

        assert len(m.layers) == 2

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

        assert len(m.layers) == 2

        return

    def test_get_basemap_list(self):

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

    def test_get_viz_params(self, asset_image_viz):

        image = ee.Image(asset_image_viz)

        res = sm.SepalMap.get_viz_params(image)

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

    def test_remove_layer(self, ee_map_with_layers):

        m = ee_map_with_layers

        # remove using a layer without counting the base
        m.remove_layer(0)
        assert len(m.layers) == 4
        assert m.layers[0].base is True

        # remove when authorizing selection of bases
        m.remove_layer(0, base=True)
        assert len(m.layers) == 3
        assert m.layers[0].name == "Classification"

        return

    def test_remove_all(self, ee_map_with_layers):

        m = ee_map_with_layers

        m.remove_all()
        assert len(m.layers) == 1

        m.remove_all(base=True)
        assert len(m.layers) == 0

        return

    def test_add_layer(self):

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
        geojson = GeoJSON(data=polygon)

        # Act
        m.add_layer(geojson, hover=True)

        # Assert
        new_layer = m.layers[-1]

        layer_style = json.loads((ss.JSON_DIR / "layer.json").read_text())["layer"]
        hover_style = json.loads((ss.JSON_DIR / "layer_hover.json").read_text())

        assert all([new_layer.style[k] == v for k, v in layer_style.items()])
        assert all([new_layer.hover_style[k] == v for k, v in hover_style.items()])

        # Arrange with style
        layer_style = {"color": "blue"}
        layer_hover_style = {"color": "red"}
        geojson = GeoJSON(
            data=polygon, style=layer_style, hover_style=layer_hover_style
        )

        # Act
        m.add_layer(geojson)

        # Assert
        new_layer = m.layers[-1]

        assert new_layer.style == layer_style
        assert new_layer.hover_style == layer_hover_style

    def test_add_basemap(self):

        m = sm.SepalMap()
        m.add_basemap("HYBRID")

        assert len(m.layers) == 2
        assert m.layers[1].name == "Google Satellite"
        assert m.layers[1].base is True

        # check that a wrong layer raise an error if it's not part of the leaflet basemap list
        with pytest.raises(Exception):
            m.add_basemap("TOTO")

        return

    def test_get_scale(self):

        m = sm.SepalMap()
        m.zoom = 5

        assert math.isclose(m.get_scale(), 4891.97)

        return

    def test_find_layer(self, ee_map_with_layers):

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
        res = m.find_layer(0)
        assert res.name == "NDWI harmonics"

        res = m.find_layer(-1)
        assert res.name == "RGB"

        # out of bounds
        with pytest.raises(ValueError):
            res = m.find_layer(50)

        # search by layer
        res = m.find_layer(m.layers[2])
        assert res.name == "Classification"

        # search including the basemap
        res = m.find_layer(0, base=True)
        assert "Carto" in res.name
        assert res.base is True

        # search something that is not a key
        with pytest.raises(ValueError):
            m.find_layer(m)

        return

    @pytest.mark.skipif(
        is_set_localtileserver is False,
        reason="localtileserver implementation is still in beta",
    )
    def test_zoom_raster(self, byte):

        m = sm.SepalMap()
        layer = m.add_raster(byte)
        m.zoom_raster(layer)

        center = [33.89703655465772, -117.63458938969723]
        assert all([math.isclose(s, t, rel_tol=0.2) for s, t in zip(m.center, center)])
        assert m.zoom == 15.0

        return

    def test_add_legend(self, ee_map_with_layers):

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

    @pytest.fixture
    def rgb(self):
        """add a raster file of the bahamas coming from rasterio test suit"""

        rgb = Path.home() / "rgb.tif"

        if not rgb.is_file():
            file = "https://raw.githubusercontent.com/rasterio/rasterio/master/tests/data/RGB.byte.tif"
            urlretrieve(file, rgb)

        yield rgb

        rgb.unlink()

        return

    @pytest.fixture
    def byte(self):
        """add a raster file of the bahamas coming from rasterio test suit"""

        rgb = Path.home() / "byte.tif"

        if not rgb.is_file():
            file = "https://raw.githubusercontent.com/rasterio/rasterio/master/tests/data/byte.tif"
            urlretrieve(file, rgb)

        yield rgb

        rgb.unlink()

        return

    @pytest.fixture
    def ee_map_with_layers(self, asset_image_viz):

        image = ee.Image(asset_image_viz)
        m = sm.SepalMap()

        # display all the viz available in the image
        for viz in sm.SepalMap.get_viz_params(image).values():
            m.addLayer(image, {}, viz["name"], viz_name=viz["name"])

        return m
