from urllib.request import urlretrieve
from zipfile import ZipFile

import ee
import pytest

from sepal_ui import aoi


class TestAoiModel:
    def test_init_no_ee(self, alert, fake_vector):

        # default init
        aoi_model = aoi.AoiModel(alert, gee=False)
        assert isinstance(aoi_model, aoi.AoiModel)
        assert aoi_model.ee is False

        # with a default vector
        aoi_model = aoi.AoiModel(alert, vector=fake_vector, gee=False)
        assert aoi_model.name == "gadm36_VAT_0"

        # test with a non ee admin
        admin = "VAT"  # GADM Vatican city
        aoi_model = aoi.AoiModel(alert, gee=False, admin=admin)

        assert aoi_model.name == "VAT"

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_init_ee(alert, gee_dir):

        # default init
        aoi_model = aoi.AoiModel(alert, folder=gee_dir)
        assert isinstance(aoi_model, aoi.AoiModel)
        assert aoi_model.ee is True

        # with default assetId
        asset_id = str(gee_dir / "feature_collection")
        aoi_model = aoi.AoiModel(alert, asset=asset_id, folder=gee_dir)

        assert aoi_model.asset_name["pathname"] == asset_id
        assert aoi_model.default_asset["pathname"] == asset_id
        assert all(aoi_model.gdf) is not None
        assert aoi_model.feature_collection is not None
        assert aoi_model.name == "feature_collection"

        # check that wrongly defined asset_name raise errors
        with pytest.raises(Exception):
            aoi_model = aoi.AoiModel(alert, folder=gee_dir)
            aoi_model._from_asset({"pathname": None})

        with pytest.raises(Exception):
            aoi_model = aoi.AoiModel(alert, folder=gee_dir)
            asset = {"pathname": asset_id, "column": "data", "value": None}
            aoi_model._from_asset(asset)

        # it should be the same with a different name
        aoi_model = aoi.AoiModel(alert, folder=gee_dir)
        asset = {"pathname": asset_id, "column": "data", "value": 0}
        aoi_model._from_asset(asset)
        assert aoi_model.name == "feature_collection_data_0"

        # with a default admin
        admin = 110  # GAUL Vatican city
        aoi_model = aoi.AoiModel(alert, admin=admin, folder=gee_dir)
        assert aoi_model.name == "VAT"

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_get_columns(self, test_model, test_columns):

        # test that before any data is set the method raise an error
        with pytest.raises(Exception):
            aoi_model = aoi.AoiModel()
            aoi_model.get_columns()

        # test data
        res = test_model.get_columns()
        assert res == test_columns

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_get_fields(self, test_model):

        # test that before any data is set the method raise an error
        with pytest.raises(Exception):
            aoi_model = aoi.AoiModel()
            aoi_model.get_fields("toto")

        # init
        column = "ADM0_CODE"
        res = test_model.get_fields(column)
        assert res == [110]

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_get_selected(self, test_model):

        # test that before any data is set the method raise an error
        with pytest.raises(Exception):
            aoi_model = aoi.AoiModel()
            aoi_model.get_fields("toto", "toto")

        # select the vatican feature in GAUL 2015
        ee_vat = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(
            ee.Filter.eq("ADM0_CODE", 110)
        )

        # select the geometry associated with Vatican city (all of it)
        column, field = ("ADM0_CODE", 110)
        feature = test_model.get_selected(column, field)

        # assert they are the same
        dif = feature.geometry().difference(ee_vat.geometry()).coordinates().length()
        assert dif.getInfo() == 0

        return

    def test_clear_attributes(self, alert, aoi_model_outputs, aoi_model_traits):

        aoi_model = aoi.AoiModel(alert, gee=False)

        # insert dum parameter everywhere
        dum = "dum"
        [setattr(aoi_model, trait, dum) for trait in aoi_model_traits]
        [setattr(aoi_model, out, dum) for out in aoi_model_outputs]

        # clear all the parameters
        aoi_model.clear_attributes()

        # create a function for readability
        def is_none(member):
            return getattr(aoi_model, member) is None

        assert all([is_none(trait) for trait in aoi_model_traits])
        assert all([is_none(out) for out in aoi_model_outputs])

        # check that default are saved
        aoi_model = aoi.AoiModel(alert, admin="VAT", gee=False)  # GADM for Vatican

        # insert dummy parameter
        [setattr(aoi_model, trait, dum) for trait in aoi_model_traits]
        [setattr(aoi_model, out, dum) for out in aoi_model_outputs]

        # clear
        aoi_model.clear_attributes()

        # assert that it's still Vatican
        assert aoi_model.name == "VAT"

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_total_bounds(self, test_model, test_bounds):

        bounds = test_model.total_bounds()
        assert bounds == test_bounds

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_clear_output(self, test_model, aoi_model_outputs):

        # create functions for readability
        def is_not_none(member):
            return getattr(test_model, member) is not None

        def is_none(member):
            return getattr(test_model, member) is None

        # test that the data are not all empty
        assert any([is_not_none(out) for out in aoi_model_outputs])

        # clear the aoi outputs
        test_model.clear_output()
        assert all([is_none(out) for out in aoi_model_outputs])

        return

    def test_set_object(self, alert):

        aoi_model = aoi.AoiModel(alert, gee=False)

        # test that no method returns an error
        with pytest.raises(Exception):
            aoi_model.set_object()

        return

    def test_from_admin(self, alert, gee_dir):

        aoi_model = aoi.AoiModel(alert, folder=gee_dir)

        # with fake number
        with pytest.raises(Exception):
            aoi_model._from_admin(0)

        # test france
        aoi_model._from_admin(110)
        assert aoi_model.name == "VAT"

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_from_point(self, alert, fake_points, gee_dir):

        aoi_model = aoi.AoiModel(alert, folder=gee_dir, gee=False)

        # uncomplete json
        points = {
            "pathname": None,
            "id_column": "id",
            "lat_column": "lat",
            "lng_column": "lon",
        }
        with pytest.raises(Exception):
            aoi_model._from_points(points)

        # complete
        points = {
            "pathname": fake_points,
            "id_column": "id",
            "lat_column": "lat",
            "lng_column": "lon",
        }
        aoi_model._from_points(points)
        assert aoi_model.name == "point"

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_from_vector(self, alert, gee_dir, fake_vector):

        aoi_model = aoi.AoiModel(alert, folder=gee_dir, gee=False)

        # with no pathname
        with pytest.raises(Exception):
            aoi_model._from_vector(fake_vector)

        # only pathname and all
        vector = {"pathname": fake_vector, "column": "ALL", "value": None}
        aoi_model._from_vector(vector)
        assert aoi_model.name == "gadm36_VAT_0"

        # all params
        vector = {"pathname": fake_vector, "column": "GID_0", "value": "VAT"}
        aoi_model._from_vector(vector)
        assert aoi_model.name == "gadm36_VAT_0_GID_0_VAT"

        # missing value
        vector = {"pathname": fake_vector, "column": "GID_0", "value": None}
        with pytest.raises(Exception):
            aoi_model._from_vector(vector)

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_from_geo_json(self, alert, gee_dir, square):

        aoi_model = aoi.AoiModel(alert, folder=gee_dir, gee=False)

        # no points
        with pytest.raises(Exception):
            aoi_model._from_geo_json({})

        # fully qualified square
        aoi_model.name = "square"
        aoi_model._from_geo_json(square)
        assert aoi_model.name == "square"

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_from_asset(self, alert, gee_dir):

        # init parameters
        asset_id = str(gee_dir / "feature_collection")
        aoi_model = aoi.AoiModel(alert, folder=gee_dir)

        # no asset name
        with pytest.raises(Exception):
            aoi_model._from_asset(asset_id)

        # only pathname and all
        asset = {"pathname": asset_id, "column": "ALL", "value": None}
        aoi_model._from_asset(asset)
        assert aoi_model.name == "feature_collection"

        # all params
        asset = {"pathname": asset_id, "column": "data", "value": 0}
        aoi_model._from_asset(asset)
        assert aoi_model.name == "feature_collection_data_0"

        # missing value
        asset = {"pathname": asset_id, "column": "data", "value": None}

        with pytest.raises(Exception):
            aoi_model._from_asset(asset)

        return

    @pytest.fixture(scope="class")
    def square(self):
        """a geojson square around the vatican city"""

        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [12.445173, 41.899176],
                                [12.445173, 41.908813],
                                [12.4592, 41.908813],
                                [12.4592, 41.899176],
                                [12.445173, 41.899176],
                            ]
                        ],
                    },
                }
            ],
        }

    @pytest.fixture(scope="class")
    def fake_points(self, tmp_dir):
        """create a fake point file the tmp file will be destroyed after the tests"""

        file = tmp_dir / "point.csv"
        with file.open("w") as f:
            f.write("lat,lon,id\n")
            f.write("1,1,0\n")
            f.write("0,0,1\n")

        yield file

        file.unlink()

        return

    @pytest.fixture(scope="class")
    def fake_vector(self, tmp_dir):
        """create a fake vector file from the GADM definition of vatican city and save it in the tmp dir. the tmp files will be destroyed after the test."""

        # download vatican city from GADM
        file = tmp_dir / "test.zip"

        gadm_vat_link = "https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_VAT_shp.zip"
        name = "gadm36_VAT_0"

        urlretrieve(gadm_vat_link, file)

        with ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(tmp_dir)

        file.unlink()

        yield tmp_dir / f"{name}.shp"

        # destroy the file after the test
        [f.unlink() for f in tmp_dir.glob(f"{name}.*")]

        return

    @pytest.fixture
    def test_model(self, alert, gee_dir):
        """
        Create a test AoiModel based on GEE using Vatican
        """
        admin = 110  # vatican city (smalest adm0 feature)
        return aoi.AoiModel(alert, admin=admin, folder=gee_dir)

    @pytest.fixture(scope="class")
    def aoi_model_traits(self):
        """return the list of an aoi model traits"""

        return [
            "method",
            "point_json",
            "vector_json",
            "geo_json",
            "admin",
            "asset_name",
            "name",
        ]

    @pytest.fixture(scope="class")
    def aoi_model_outputs(self):
        """return the list of an aoi model outputs"""

        return [
            "gdf",
            "feature_collection",
            "ipygeojson",
            "selected_feature",
            "dst_asset_id",
        ]

    @pytest.fixture(scope="class")
    def test_columns(self):
        """return the column of the test vatican aoi"""
        return [
            "ADM0_CODE",
            "ADM0_NAME",
            "DISP_AREA",
            "EXP0_YEAR",
            "STATUS",
            "STR0_YEAR",
            "Shape_Leng",
        ]

    @pytest.fixture(scope="class")
    def test_bounds(self):
        """return the bounds of the vatican asset"""

        return (
            12.445770205631668,
            41.90021953934405,
            12.457671530175347,
            41.90667181034752,
        )
