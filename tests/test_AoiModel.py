from urllib.request import urlretrieve
from zipfile import ZipFile

import ee
import pytest

from sepal_ui import aoi


class TestAoiModel:
    def test_init(self, alert, gee_dir, asset_italy, fake_vector):

        # default init
        aoi_model = aoi.AoiModel(alert, folder=gee_dir)
        assert isinstance(aoi_model, aoi.AoiModel)
        assert aoi_model.ee is True

        # with default assetId
        fao_gaul_0 = "FAO/GAUL/2015/level0"
        aoi_model = aoi.AoiModel(alert, asset=fao_gaul_0, folder=gee_dir)

        assert aoi_model.asset_name["pathname"] == fao_gaul_0
        assert aoi_model.default_asset["pathname"] == fao_gaul_0
        assert all(aoi_model.gdf) is not None
        assert aoi_model.feature_collection is not None
        assert aoi_model.name == "level0"

        # check that wrongly defined asset_name raise errors
        with pytest.raises(Exception):
            aoi_model = aoi.AoiModel(alert, folder=gee_dir)
            aoi_model._from_asset({"pathname": None})

        with pytest.raises(Exception):
            aoi_model = aoi.AoiModel(alert, folder=gee_dir)
            aoi_model._from_asset(
                {"pathname": fao_gaul_0, "column": "ADM0_CODE", "value": None}
            )

        # it should be the same with a different name
        aoi_model = aoi.AoiModel(alert, folder=gee_dir)
        aoi_model._from_asset(
            {"pathname": fao_gaul_0, "column": "ADM0_CODE", "value": 110}
        )
        assert aoi_model.name == "level0_ADM0_CODE_110"

        # with a default admin
        admin = 110  # GAUL France
        aoi_model = aoi.AoiModel(alert, admin=admin, folder=gee_dir)
        assert aoi_model.name == "VAT"

        # with a default vector
        aoi_model = aoi.AoiModel(alert, vector=fake_vector, gee=False)
        assert aoi_model.name == "gadm36_VAT_0"

        # test with a non ee definition
        admin = "VAT"  # GADM France
        aoi_model = aoi.AoiModel(alert, gee=False, admin=admin)

        assert aoi_model.name == "VAT"

        return

    def test_get_columns(self, test_model):

        # test that before any data is set the method raise an error
        with pytest.raises(Exception):
            aoi_model = aoi.AoiModel()
            aoi_model.get_columns()

        # test data
        test_data = [
            "ADM0_CODE",
            "ADM0_NAME",
            "DISP_AREA",
            "EXP0_YEAR",
            "STATUS",
            "STR0_YEAR",
            "Shape_Leng",
        ]

        res = test_model.get_columns()

        assert res == test_data

        return

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

    def test_get_selected(self, test_model):

        # test that before any data is set the method raise an error
        with pytest.raises(Exception):
            aoi_model = aoi.AoiModel()
            aoi_model.get_fields("toto", "toto")

        # select the vatican feature in GAUL 2015
        ee_vat = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(
            ee.Filter.eq("ADM0_CODE", 110)
        )

        # select the geometry associated with france (all of it)
        column = "ADM0_CODE"
        field = 110
        feature = test_model.get_selected(column, field)

        # assert they are the same
        dif = feature.geometry().difference(ee_vat.geometry())
        assert dif.getInfo() == 0

        return

    def test_clear_attributes(
        self, alert, gee_dir, aoi_model_outputs, aoi_model_traits
    ):

        aoi_model = aoi.AoiModel(alert, folder=gee_dir)

        dum = "dum"

        # insert dum parameter everywhere
        [setattr(aoi_model, trait, dum) for trait in aoi_model_traits]
        [setattr(aoi_model, out, dum) for out in aoi_model_outputs]

        # create a function for readability
        def is_none(member):
            return getattr(aoi_model, member) is None

        # clear them
        aoi_model.clear_attributes()

        assert all([is_none(trait) for trait in aoi_model_traits])
        assert all([is_none(out) for out in aoi_model_outputs])

        # check that default are saved
        aoi_model = aoi.AoiModel(alert, admin=110, folder=gee_dir)  # GAUL for Vatican

        # insert dummy args
        [setattr(aoi_model, trait, dum) for trait in aoi_model_traits]
        [setattr(aoi_model, out, dum) for out in aoi_model_outputs]

        # clear
        aoi_model.clear_attributes()

        # assert that it's still Vatican
        assert aoi_model.name == "VAT"

        return

    def test_total_bounds(self, test_model):

        # test data
        expected_bounds = (
            -5.142230921252722,
            41.33878298628808,
            9.561552263332496,
            51.09281241936492,
        )

        bounds = test_model.total_bounds()

        assert bounds == expected_bounds

        return

    def test_clear_output(self, test_model, aoi_model_outputs):

        aoi_model = test_model.copy()

        # create functions for readability
        def is_not_none(member):
            return getattr(aoi_model, member) is not None

        def is_none(member):
            return getattr(aoi_model, member) is None

        # test that the data are not all empty
        assert any([is_not_none(out) for out in aoi_model_outputs])

        # clear the aoi outputs
        aoi_model.clear_output()
        assert all([is_none(out) for out in aoi_model_outputs])

        return

    def test_set_object(self, alert, gee_dir):

        aoi_model = aoi.AoiModel(alert, folder=gee_dir)

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

    def test_from_asset(self, alert, gee_dir, asset_france):

        # use the fao GAUL level 0 as test asset
        fao_gaul_0 = "FAO/GAUL/2015/level0"

        aoi_model = aoi.AoiModel(alert, folder=gee_dir)

        # no asset name
        with pytest.raises(Exception):
            aoi_model._from_asset(asset_france)

        # only pathname and all
        asset = {"pathname": fao_gaul_0, "column": "ALL", "value": None}
        aoi_model._from_asset(asset)
        assert aoi_model.name == "level0"

        # all params
        asset = {"pathname": fao_gaul_0, "column": "ADM0_CODE", "value": 110}
        aoi_model._from_asset(asset)
        assert aoi_model.name == "france_ADM0_CODE_110"

        # missing value
        asset = {"pathname": fao_gaul_0, "column": "ADM0_CODE", "value": None}
        with pytest.raises(Exception):
            aoi_model._from_asset(asset)

        return

    @pytest.fixture
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

    @pytest.fixture
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

    @pytest.fixture
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
        Create a dummy alert and a test AoiModel based on GEE using Vatican
        """
        admin = 110  # vatican city (smalest adm0 feature)
        return aoi.AoiModel(alert, admin=admin, folder=gee_dir)

    @pytest.fixture
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

    @pytest.fixture
    def aoi_model_outputs(self):
        """return the list of an aoi model outputs"""

        return [
            "gdf",
            "feature_collection",
            "ipygeojson",
            "selected_feature",
            "dst_asset_id",
        ]
