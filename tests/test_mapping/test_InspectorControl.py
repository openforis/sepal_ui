import math
from pathlib import Path
from urllib.request import urlretrieve

import ee
import geopandas as gpd
import pytest

from sepal_ui import mapping as sm


class TestInspectorControl:
    def test_init(self):

        m = sm.SepalMap()
        inspector_control = sm.InspectorControl(m)
        m.add(inspector_control)

        assert isinstance(inspector_control, sm.InspectorControl)

    def test_deprecated(self):

        m = sm.SepalMap()
        with pytest.deprecated_call():
            inspector_control = sm.ValueInspector(m)
        m.add(inspector_control)

        assert isinstance(inspector_control, sm.InspectorControl)

    def test_toogle_cursor(self):

        m = sm.SepalMap()
        inspector_control = sm.InspectorControl(m)
        m.add(inspector_control)

        # activate the window
        inspector_control.menu.v_model = True
        assert m.default_style.cursor == "crosshair"

        # close with the menu
        inspector_control.menu.v_model = False
        assert m.default_style.cursor == "grab"

        return

    def test_read_data(self):

        # not testing the display of anything here just the interaction
        m = sm.SepalMap()
        inspector_control = sm.InspectorControl(m)
        m.add(inspector_control)

        # click anywhere without activation
        inspector_control.read_data(type="click", coordinates=[0, 0])
        assert len(inspector_control.text.children) == 1

        # click when activated
        inspector_control.menu.v_model = True
        inspector_control.read_data(type="click", coordinates=[0, 0])
        assert len(inspector_control.text.children) == 4

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_free_eelayer(self, world_temp, ee_adm2):

        # create a map with a value inspector
        m = sm.SepalMap()
        inspector_control = sm.InspectorControl(m)

        # check a nodata place on Image
        data = inspector_control._from_eelayer(world_temp.mosaic(), [0, 0])
        assert data == {"temperature_2m": None}

        # check vatican city
        data = inspector_control._from_eelayer(world_temp.mosaic(), [12.457, 41.902])
        assert data == {"temperature_2m": 296.00286865234375}

        # check a featurecollection on nodata place
        data = inspector_control._from_eelayer(ee_adm2, [0, 0])
        assert data == {"ADM2_CODE": None}

        # check the featurecollection on vatican city
        data = inspector_control._from_eelayer(ee_adm2, [12.457, 41.902])
        assert data == {"ADM2_CODE": 18350}

        return

    def test_from_geojson(self, adm0_vatican):

        # create a map with a value inspector
        m = sm.SepalMap()
        inspector_control = sm.InspectorControl(m)

        # check a featurecollection on nodata place
        data = inspector_control._from_geojson(adm0_vatican, [0, 0])
        assert data == {"GID_0": None, "NAME_0": None}

        # check the featurecollection on vatican city
        data = inspector_control._from_geojson(adm0_vatican, [12.457, 41.902])
        assert data == {"GID_0": "VAT", "NAME_0": "Vatican City"}

        return

    def test_from_raster(self, raster_bahamas):

        # create a map with a value inspector
        m = sm.SepalMap()
        inspector_control = sm.InspectorControl(m)

        # check a featurecollection on nodata place
        data = inspector_control._from_raster(raster_bahamas, [0, 0])
        assert data == {"band 1": None, "band 2": None, "band 3": None}

        # check the featurecollection on vatican city
        data = inspector_control._from_raster(raster_bahamas, [-78.072, 24.769])
        assert math.isclose(data["band 1"], 70.46553, rel_tol=1e-5)
        assert math.isclose(data["band 2"], 91.41595, rel_tol=1e-5)
        assert math.isclose(data["band 3"], 93.08673, rel_tol=1e-5)

        return

    @pytest.fixture(scope="class")
    def world_temp(self):
        """get the world temperature dataset from GEE."""
        return (
            ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")
            .filter(ee.Filter.date("2020-07-01", "2020-07-02"))
            .select("temperature_2m")
        )

    @pytest.fixture(scope="class")
    def ee_adm2(self):
        """get a featurecollection with only adm2code values."""
        return ee.FeatureCollection("FAO/GAUL/2015/level2").select("ADM2_CODE")

    @pytest.fixture(scope="class")
    def raster_bahamas(self):
        """add a raster file of the bahamas coming from rasterio test suit."""
        rgb = Path.home() / "rgb.tif"

        if not rgb.is_file():
            file = "https://raw.githubusercontent.com/rasterio/rasterio/master/tests/data/RGB.byte.tif"
            urlretrieve(file, rgb)

        yield rgb

        rgb.unlink()

        return

    @pytest.fixture(scope="class")
    def adm0_vatican(self):
        """create a geojson of vatican city."""
        zip_file = Path.home() / "VAT.zip"

        if not zip_file.is_file():
            urlretrieve(
                "https://biogeo.ucdavis.edu/data/gadm3.6/gpkg/gadm36_VAT_gpkg.zip",
                zip_file,
            )

        layer_name = "gadm36_VAT_0"
        level_gdf = gpd.read_file(f"{zip_file}!gadm36_VAT.gpkg", layer=layer_name)
        geojson = level_gdf.__geo_interface__

        yield geojson

        zip_file.unlink()

        return
