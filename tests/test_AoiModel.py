import ee
from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile

from sepal_ui import aoi
from sepal_ui import sepalwidgets as sw


class TestAoiModel:

    # test folder
    FOLDER = "projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test"

    def test_init(self):

        # dummy alert
        alert = sw.Alert()

        # default init
        aoi_model = aoi.AoiModel(alert, folder=self.FOLDER)
        assert isinstance(aoi_model, aoi.AoiModel)
        assert aoi_model.ee == True

        # with default assetId
        asset_id = "users/bornToBeAlive/sepal_ui_test/italy"
        aoi_model = aoi.AoiModel(alert, asset=asset_id, folder=self.FOLDER)

        assert aoi_model.asset_name == asset_id
        assert aoi_model.default_asset == asset_id
        assert all(aoi_model.gdf) != None
        assert aoi_model.feature_collection != None
        assert aoi_model.name == "italy"

        # with a default admin
        admin = 85  # GAUL France
        aoi_model = aoi.AoiModel(alert, admin=admin, folder=self.FOLDER)
        assert aoi_model.name == "FRA"

        # with a default vector
        vector = self._create_fake_vector()
        aoi_model = aoi.AoiModel(alert, vector=vector, gee=False)
        assert aoi_model.name == "gadm36_VAT_0"

        [f.unlink() for f in Path("~").expanduser().glob(f"{vector.stem}.*")]

        # test with a non ee definition
        admin = "FRA"  # GADM France
        aoi_model = aoi.AoiModel(alert, gee=False, admin=admin, folder=self.FOLDER)

        assert aoi_model.name == "FRA"

        return

    def test_get_columns(self):

        # dummy alert
        alert = sw.Alert()

        # init
        asset_id = "users/bornToBeAlive/sepal_ui_test/france"
        aoi_model = aoi.AoiModel(alert, asset=asset_id, folder=self.FOLDER)

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

        res = aoi_model.get_columns()

        assert res == test_data

        return

    def test_get_fields(self):

        # dummy alert
        alert = sw.Alert()

        # init
        asset_id = "users/bornToBeAlive/sepal_ui_test/france"
        aoi_model = aoi.AoiModel(alert, asset=asset_id, folder=self.FOLDER)
        column = "ADM0_CODE"

        res = aoi_model.get_fields(column)

        assert res == [85]

        return

    def test_get_selected(self):

        # dummy alert
        alert = sw.Alert()

        # init
        asset_id = "users/bornToBeAlive/sepal_ui_test/france"
        aoi_model = aoi.AoiModel(alert, asset=asset_id, folder=self.FOLDER)
        ee_france = ee.FeatureCollection(asset_id)

        # select the geometry associated with france (all of it)
        column = "ADM0_CODE"
        field = 85

        feature = aoi_model.get_selected(column, field)

        feature_geom = feature.geometry().getInfo()
        france_geom = ee_france.geometry().getInfo()

        assert feature_geom == france_geom

        return

    def test_clear_attributes(self):

        # dummy alert
        alert = sw.Alert()

        aoi_model = aoi.AoiModel(alert, folder=self.FOLDER)

        dum = "dum"

        # insert dum parameter everywhere
        aoi_model.method = dum
        aoi_model.point_json = dum
        aoi_model.vector_json = dum
        aoi_model.geo_json = dum
        aoi_model.admin = dum
        aoi_model.asset_name = dum
        aoi_model.name = dum
        aoi_model.gdf = dum
        aoi_model.feature_collection = dum
        aoi_model.ipygeojson = dum

        # clear them
        aoi_model.clear_attributes()

        assert aoi_model.method == None
        assert aoi_model.point_json == None
        assert aoi_model.vector_json == None
        assert aoi_model.geo_json == None
        assert aoi_model.admin == None
        assert aoi_model.asset_name == None
        assert aoi_model.name == None
        assert aoi_model.gdf == None
        assert aoi_model.feature_collection == None
        assert aoi_model.ipygeojson == None
        assert aoi_model.default_asset == None
        assert aoi_model.default_admin == None
        assert aoi_model.default_vector == None

        # check that default are saved
        aoi_model = aoi.AoiModel(alert, admin=85, folder=self.FOLDER)  # GAUL for France

        # insert dummy args
        aoi_model.method = dum
        aoi_model.point_json = dum
        aoi_model.vector_json = dum
        aoi_model.geo_json = dum
        aoi_model.admin = dum
        aoi_model.asset_name = dum
        aoi_model.name = dum
        aoi_model.gdf = dum
        aoi_model.feature_collection = dum
        aoi_model.ipygeojson = dum

        # clear
        aoi_model.clear_attributes()

        # assert that it's still france
        assert aoi_model.name == "FRA"

        return

    def test_total_bounds(self):

        # dummy alert
        alert = sw.Alert()

        # init
        asset_id = "users/bornToBeAlive/sepal_ui_test/france"
        aoi_model = aoi.AoiModel(alert, asset=asset_id, folder=self.FOLDER)

        # test data
        expected_bounds = (
            -5.142230921252722,
            41.33878298628808,
            9.561552263332496,
            51.09281241936492,
        )

        bounds = aoi_model.total_bounds()

        assert bounds == expected_bounds

        return

    def _create_fake_vector(self):

        # download vatican city from GADM
        root_dir = Path("~").expanduser()
        file = root_dir / "test.zip"

        gadm_vat_link = "https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_VAT_shp.zip"
        name = "gadm36_VAT_0"

        urlretrieve(gadm_vat_link, file)

        with ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(root_dir)

        file.unlink()

        return root_dir / f"{name}.shp"


if __name__ == "__main__":
    unittest.main()
