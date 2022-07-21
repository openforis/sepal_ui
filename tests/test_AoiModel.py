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
        aoi_model = aoi.AoiModel(alert, asset=asset_italy, folder=gee_dir)

        assert aoi_model.asset_name["pathname"] == asset_italy
        assert aoi_model.default_asset["pathname"] == asset_italy
        assert all(aoi_model.gdf) is not None
        assert aoi_model.feature_collection is not None
        assert aoi_model.name == "italy"

        # chack that wrongly defined asset_name raise errors
        with pytest.raises(Exception):
            aoi_model = aoi.AoiModel(alert, folder=gee_dir)
            aoi_model._from_asset({"pathname": None})

        with pytest.raises(Exception):
            aoi_model = aoi.AoiModel(alert, folder=gee_dir)
            aoi_model._from_asset(
                {"pathname": asset_italy, "column": "ADM0_CODE", "value": None}
            )

            # it should be the same with a different name
            aoi_model = aoi.AoiModel(alert, folder=gee_dir)
            aoi_model._from_asset(
                {"pathname": asset_italy, "column": "ADM0_CODE", "value": 122}
            )
            assert aoi_model.name == "italy_ADM0_CODE_122"

        # with a default admin
        admin = 85  # GAUL France
        aoi_model = aoi.AoiModel(alert, admin=admin, folder=gee_dir)
        assert aoi_model.name == "FRA"

        # with a default vector
        aoi_model = aoi.AoiModel(alert, vector=fake_vector, gee=False)
        assert aoi_model.name == "gadm36_VAT_0"

        # test with a non ee definition
        admin = "FRA"  # GADM France
        aoi_model = aoi.AoiModel(alert, gee=False, admin=admin)

        assert aoi_model.name == "FRA"

        return

    def test_get_columns(self, aoi_model_france):

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

        res = aoi_model_france.get_columns()

        assert res == test_data

        return

    def test_get_fields(self, aoi_model_france):

        # test that before any data is set the method raise an error
        with pytest.raises(Exception):
            aoi_model = aoi.AoiModel()
            aoi_model.get_fields("toto")

        # init
        column = "ADM0_CODE"

        res = aoi_model_france.get_fields(column)

        assert res == [85]

        return

    def test_get_selected(self, aoi_model_france, asset_france):

        # test that before any data is set the method raise an error
        with pytest.raises(Exception):
            aoi_model = aoi.AoiModel()
            aoi_model.get_fields("toto", "toto")

        # init
        ee_france = ee.FeatureCollection(asset_france)

        # select the geometry associated with france (all of it)
        column = "ADM0_CODE"
        field = 85

        feature = aoi_model_france.get_selected(column, field)

        feature_geom = feature.geometry().getInfo()
        france_geom = ee_france.geometry().getInfo()

        assert feature_geom == france_geom

        return

    def test_clear_attributes(
        self, alert, gee_dir, aoi_model_outputs, aoi_model_traits
    ):

        aoi_model = aoi.AoiModel(alert, folder=gee_dir)

        dum = "dum"

        # insert dum parameter everywhere
        [setattr(aoi_model, trait, dum) for trait in aoi_model_traits]
        [setattr(aoi_model, out, dum) for out in aoi_model_outputs]

        # clear them
        aoi_model.clear_attributes()

        assert all([getattr(aoi_model, trait) is None for trait in aoi_model_traits])
        assert all([getattr(aoi_model, out) is None for out in aoi_model_outputs])

        # check that default are saved
        aoi_model = aoi.AoiModel(alert, admin=85, folder=gee_dir)  # GAUL for France

        # insert dummy args
        [setattr(aoi_model, trait, dum) for trait in aoi_model_traits]
        [setattr(aoi_model, out, dum) for out in aoi_model_outputs]

        # clear
        aoi_model.clear_attributes()

        # assert that it's still france
        assert aoi_model.name == "FRA"

        return

    def test_total_bounds(self, aoi_model_france):

        # test data
        expected_bounds = (
            -5.142230921252722,
            41.33878298628808,
            9.561552263332496,
            51.09281241936492,
        )

        bounds = aoi_model_france.total_bounds()

        assert bounds == expected_bounds

        return

    def test_clear_output(self, aoi_model_france, aoi_model_outputs):

        # test that the data are not all empty
        assert any(
            [getattr(aoi_model_france, out) is not None for out in aoi_model_outputs]
        )

        # clear the aoi outputs
        aoi_model_france.clear_output()
        assert all(
            [getattr(aoi_model_france, out) is None for out in aoi_model_outputs]
        )

        return

    def test_set_object(
        self, alert, gee_dir, fake_vector, asset_france, fake_points, square
    ):

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
        aoi_model._from_admin(85)
        assert aoi_model.name == "FRA"

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

        aoi_model = aoi.AoiModel(alert, folder=gee_dir)

        # no asset name
        with pytest.raises(Exception):
            aoi_model._from_asset(asset_france)

        # only pathname and all
        asset = {"pathname": asset_france, "column": "ALL", "value": None}
        aoi_model._from_asset(asset)
        assert aoi_model.name == "france"

        # all params
        asset = {"pathname": asset_france, "column": "ADM0_CODE", "value": 85}
        aoi_model._from_asset(asset)
        assert aoi_model.name == "france_ADM0_CODE_85"

        # missing value
        asset = {"pathname": asset_france, "column": "ADM0_CODE", "value": None}
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
    def aoi_model_france(self, alert, gee_dir, asset_france):
        """create a dummy alert and a test aoi model based on GEE that use the france asset available on the test account"""

        return aoi.AoiModel(alert, asset=asset_france, folder=gee_dir)

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
