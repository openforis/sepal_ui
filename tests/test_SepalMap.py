import zipfile
from pathlib import Path
import requests
import sys

import pytest
import ee
import geemap
from ipyleaflet import basemaps, basemap_to_tiles

from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw


class TestSepalMap:
    def test_init(self):

        # check that the map start with no info
        m = sm.SepalMap()

        assert isinstance(m, sm.SepalMap)
        assert m.center == [0, 0]
        assert m.zoom == 2
        assert len(m.layers) == 1
        assert m.layers[0].name == "CartoDB.DarkMatter"
        assert m.state.viz == False
        assert isinstance(m.state, sw.StateBar)
        assert m.state.nb_layer == 1  # the basemap
        assert len(m.controls) == 6  # only thing I can check

        # check that the map start with a DC
        m = sm.SepalMap(dc=True)
        assert isinstance(m.dc, geemap.DrawControl)

        # check that the map start with several basemaps
        basemaps = ["CartoDB.DarkMatter", "CartoDB.Positron"]
        m = sm.SepalMap(basemaps)
        assert len(m.layers) == 2
        layers_name = [layer.name for layer in m.layers]
        assert all(b in layers_name for b in basemaps)

        # check that the map starts with a vinspector
        m = sm.SepalMap(vinspector=True)
        assert isinstance(m, sm.SepalMap)

        # check that the map start with a statebar
        m = sm.SepalMap(statebar=True)
        assert m.state.viz == True

        # check that a wrong layer raise an error if it's not part of the leaflet basemap list
        with pytest.raises(Exception):
            m = sm.SepalMap(["TOTO"])

        return

    def test_set_drawing_controls(self):

        m = sm.SepalMap()

        # check that the dc is not add on false
        res = m.set_drawing_controls(False)

        assert res == m
        assert not any(isinstance(c, geemap.DrawControl) for c in m.controls)

        m.set_drawing_controls(True)
        assert isinstance(m.dc, geemap.DrawControl)
        assert m.dc.rectangle == {"shapeOptions": {"color": "#79B1C9"}}
        assert m.dc.polygon == {"shapeOptions": {"color": "#79B1C9"}}
        assert m.dc.marker == {}
        assert m.dc.polyline == {}

        return

    @pytest.mark.skip(reason="problem dealing with local rasters")
    def test_remove_local_raster(self):
        # init
        m = sm.SepalMap()

        # download the raster
        out_dir = Path.home()
        dem = out_dir / "dem.tif"

        if not dem.isfile():
            dem_url = "https://drive.google.com/file/d/1vRkAWQYsLWCi6vcTMk8vLxoXMFbdMFn8/view?usp=sharing"
            geemap.download_from_gdrive(dem_url, "dem.tif", out_dir, unzip=False)

        # add a raster
        m.add_raster(dem, colormap="terrain", layer_name="DEM")

        # remove it using its name
        res = m._remove_local_raster("DEM")

        assert res == m
        assert len(m.loaded_rasters) == 0

        # remove the file
        dem.unlink()

        return

    def test_remove_last_layer(self):

        # init
        m = sm.SepalMap()

        # there is just one (the basemap) so not supposed to move
        res = m.remove_last_layer()

        assert res == m
        assert len(m.layers) == 1

        # add 1 layer and remove it
        layer = basemap_to_tiles(basemaps.CartoDB.Positron)
        m.add_layer(layer)
        m.remove_last_layer()

        assert len(m.layers) == 1

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

    @pytest.mark.skip(reason="problem dealing with local rasters")
    def test_add_raster(self):

        # create a map
        m = sm.SepalMap()

        # load a 1 band raster
        out_dir = Path.home()
        name = "dem"
        dem = out_dir / "dem.tif"
        if not dem.is_file():
            dem_url = "https://drive.google.com/file/d/1vRkAWQYsLWCi6vcTMk8vLxoXMFbdMFn8/view?usp=sharing"
            geemap.download_from_gdrive(dem_url, "dem.tif", out_dir, unzip=False)
        m.add_raster(dem, layer_name=name)

        # check name
        assert name in m.loaded_layers
        # check the colormap
        # check opacity

        # add the same one
        m.add_raster(dem, layer_name=name)

        # check that repeated name lead to specific strings

        # load a multiband file
        name = "landsat"
        opacity = 0.5
        landsat = out_dir / "landsat.tif"
        if not landsat.is_file():
            landsat_url = "https://drive.google.com/file/d/1EV38RjNxdwEozjc9m0FcO3LFgAoAX1Uw/view?usp=sharing"
            geemap.download_from_gdrive(
                landsat_url, "landsat.tif", out_dir, unzip=False
            )
        m.add_raster(landsat, layer_name=name, opacity=opacity)

        # check that it's displayed
        # force opacity of the layer

        m.add_raster(landsat, layer_name=name, opacity=14)

        # test > 1 opacity settings

        return

    def test_show_dc(self):

        # add a map with a dc
        m = sm.SepalMap(dc=True)

        # draw something

        # show dc
        res = m.show_dc()

        assert res == m
        assert m.dc in m.controls

        return

    def hide_dc(self):

        # add a map with a dc
        m = sm.SepalMap(dc=True)

        # show dc
        m.show_dc()

        # hide it
        res = m.hide_dc()

        assert res == m
        assert m.dc not in m.controls

        return

    def test_change_cursor(self):

        # add a map
        m = sm.SepalMap()

        # change the vinspector trait
        m.vinspector = True
        assert m.default_style.get_state("cursor") == {"cursor": "crosshair"}

        # change it back
        m.vinspector = False
        assert m.default_style.get_state("cursor") == {"cursor": "grab"}

        return

    def test_get_basemap_list(self):

        res = sm.SepalMap.get_basemap_list()

        assert isinstance(res, list)

        return

    def test_add_colorbar(self):

        # create a map and add a colorbar
        m = sm.SepalMap()
        m.add_colorbar(colors=["#fc8d59", "#ffffbf", "#91bfdb"], vmin=0, vmax=5)

        assert len(m.controls) == 7  # only thing I can check

        return
