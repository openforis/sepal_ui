from copy import deepcopy
from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile

import ee
import geopandas as gpd
import pytest
from sepal_ui import aoi
from sepal_ui.reclassify import ReclassifyModel
from sepal_ui.scripts import gee


class TestReclassifyModel:
    def test_gee_init(self, model_gee):

        assert isinstance(model_gee, ReclassifyModel)
        assert model_gee.gee is True

        return

    def test_local_init(self, model_local):

        assert isinstance(model_local, ReclassifyModel)
        assert model_local.gee is False

        return

    def test_get_classes(self, model_gee, reclass_file):
        """Test if the matrix is saved and corresponds with the the output"""

        with pytest.raises(Exception):
            model_gee.dst_class_file = "I/dont/exist.nothing"
            model_gee.get_classes()

        # Arrange
        expected_class_dict = {
            1: ("Forest", "#044D02"),
            2: ("Grassland", "#F5FF00"),
            3: ("Cropland", "#FF8100"),
            4: ("Wetland", "#0013FF"),
            5: ("Settlement", "#FFFFFF"),
            6: ("Other land", "#FF00DE"),
        }

        # Act
        model_gee.dst_class_file = str(reclass_file)
        class_dict = model_gee.get_classes()

        # Assert
        assert class_dict == expected_class_dict

        return

    def test_get_type_gee(self, model_gee, model_gee_vector, model_gee_image):
        """Tests the asset type with gee"""

        # Test without source
        with pytest.raises(Exception):
            model_gee.get_type()

        with pytest.raises(Exception):
            model_gee.src_gee = "I/dont/exist"
            model_gee.get_type()

        # test vector
        assert model_gee_vector.get_type() is False

        # Test images
        assert model_gee_image.get_type() is True

        return

    def test_get_type_local(self, model_local, model_local_vector, model_local_image):
        """Tests the asset type without gee"""

        # Test no input
        with pytest.raises(Exception):
            model_local.get_type()

        # Test with a local vector. Let's use the model
        assert model_local_vector.get_type() is False

        # Test with a local image
        assert model_local_image.get_type() is True

        return

    def test_get_bands_gee(self, model_gee_vector, model_gee_image):
        """check if the bands are correctly retreived"""

        # Arrange
        table_bands = ["APOYO", "AREA_HA", "CAMBIO", "CODIGO"]
        image_bands = ["y1992", "y1993", "y1994"]

        # Act - Assert
        assert model_gee_vector.get_bands() == table_bands
        assert model_gee_image.get_bands() == image_bands

        return

    def test_get_bands_local(self, model_local_vector, model_local_image):

        table_bands = ["BoroCode", "BoroName", "Shape_Area", "Shape_Leng"]
        image_bands = [1]

        assert model_local_vector.get_bands() == table_bands
        assert model_local_image.get_bands() == image_bands

        return

    def test_get_aoi(self, model_gee):

        # default to error if no asset is set in the aoi_model
        with pytest.raises(Exception):
            assert model_gee.get_aoi() is None

        # Test when there is an aoi but there is not a feature collection selected
        model_gee.enforce_aoi = False
        assert model_gee.get_aoi() is None

        # set the aoi to france
        model_gee.aoi_model._from_admin(85)  # france
        assert model_gee.get_aoi() is not None

        return

    def test_unique_gee_image(self, model_gee_image, asset_image_aoi, no_name):

        # Unique values when not using an area of interes
        image_unique = [
            10,
            11,
            30,
            40,
            50,
            60,
            100,
            110,
            120,
            130,
            150,
            160,
            180,
            190,
            210,
        ]

        # Unique values when using a sample area of interest
        image_unique_aoi = [30, 40, 50, 100, 110, 120, 130, 160]

        model_gee_image.band = "y1992"
        model_gee_image.aoi_model._from_asset(
            {"pathname": asset_image_aoi, "column": "ALL", "value": None}
        )
        print(model_gee_image.aoi_model.name)
        assert model_gee_image.unique() == {str(i): no_name for i in image_unique_aoi}

        model_gee_image.aoi_model = None
        assert model_gee_image.unique() == {str(i): no_name for i in image_unique}

        return

    def test_unique_gee_vector(self, model_gee_vector, asset_table_aoi, no_name):

        # Unique values when not using an area of interest
        vector_unique = [
            111,
            112,
            231,
            232,
            233,
            242,
            243,
            244,
            245,
            313,
            314,
            323,
            333,
            334,
            511,
            512,
            1312,
            2121,
            2141,
            2232,
            3131,
            3132,
            3221,
            3222,
            3231,
            3232,
            31111,
            31121,
            31211,
            31221,
            32111,
            32112,
        ]

        # Unique values when using an area of interest
        vector_unique_aoi = [
            231,
            233,
            242,
            243,
            244,
            313,
            323,
            511,
            3131,
            3132,
            3221,
            3231,
            3232,
            31111,
        ]

        model_gee_vector.band = "CODIGO"
        model_gee_vector.aoi_model._from_asset(
            {"pathname": asset_table_aoi, "column": "ALL", "value": None}
        )
        assert model_gee_vector.unique() == {i: no_name for i in vector_unique_aoi}

        model_gee_vector.aoi_model = None
        model_gee_vector.band = "CODIGO"
        assert model_gee_vector.unique() == {i: no_name for i in vector_unique}

        return

    def test_unique_local_image(self, model_local_image, no_name):

        image_unique = [1, 2, 3]

        model_local_image.band = 1
        assert model_local_image.unique() == {i: no_name for i in image_unique}

        # TODO: We have to create the method to clip the local vector/images

        return

    def test_unique_local_vector(self, model_local_vector, no_name):

        vector_unique = [1, 2, 3, 4, 5]

        model_local_vector.band = "BoroCode"
        assert model_local_vector.unique() == {i: no_name for i in vector_unique}

        return

    def test_reclassify_initial_exceptions(self, model_gee_image):

        # Test reclassify method without matrix
        with pytest.raises(Exception):
            model_gee_image.reclassify()

        # Test reclassify method without band
        with pytest.raises(Exception):
            model_gee_image.matrix = {1: 1}
            model_gee_image.reclassify()

        # test reclassify without setting an aoi
        with pytest.raises(Exception):
            model_gee_image.matrix = {1: 1}
            model_gee_image.band = "y1992"
            model_gee_image.reclassify()

        return

    def test_reclassify_gee_vector(self, model_gee_vector, asset_table_aoi, alert):
        """Test reclassification of vectors when using an area of interest"""

        unique_value = [
            231,
            233,
            242,
            243,
            244,
            313,
            323,
            511,
            3131,
            3132,
            3221,
            3231,
            3232,
            31111,
        ]
        matrix = {v: 2 * i // len(unique_value) for i, v in enumerate(unique_value)}

        model_gee_vector.matrix = matrix
        model_gee_vector.band = "CODIGO"
        model_gee_vector.aoi_model._from_asset(
            {"pathname": asset_table_aoi, "column": "ALL", "value": None}
        )
        model_gee_vector.reclassify()

        if model_gee_vector.save:

            assert model_gee_vector.dst_gee == f"{model_gee_vector.src_gee}_reclass"

            # delete the created file
            description = Path(model_gee_vector.dst_gee).stem
            gee.wait_for_completion(description, alert)
            ee.data.deleteAsset(model_gee_vector.dst_gee)
        else:

            assert model_gee_vector.dst_gee_memory is not None

        return

    def test_reclassify_gee_image(self, model_gee_image, asset_image_aoi, alert):
        """Test reclassification of vectors when using an area of interest"""

        unique_value = [30, 40, 50, 100, 110, 120, 130, 160]
        matrix = {
            v: 2 * (i // len(unique_value) + 1) for i, v in enumerate(unique_value)
        }

        model_gee_image.matrix = matrix
        model_gee_image.band = "y1992"
        model_gee_image.aoi_model._from_asset(
            {"pathname": asset_image_aoi, "column": "ALL", "value": None}
        )
        model_gee_image.reclassify()

        if model_gee_image.save:

            assert model_gee_image.dst_gee == f"{model_gee_image.src_gee}_reclass"

            # delete the created file
            description = Path(model_gee_image.dst_gee).stem
            gee.wait_for_completion(description, alert)
            ee.data.deleteAsset(model_gee_image.dst_gee)

        else:

            assert model_gee_image.dst_gee_memory is not None

        return

    def test_reclassify_local_image(self, model_local_image, tmp_dir):

        # Create a dummy translation matrix for local image
        matrix = {1: 4, 2: 5, 3: 6}

        model_local_image.matrix = matrix
        model_local_image.band = 1
        model_local_image.reclassify()

        dst = tmp_dir / f"{Path(model_local_image.src_local).stem}_reclass.tif"

        assert model_local_image.dst_local == str(dst)

        # remove the created file
        Path(model_local_image.dst_local).unlink()

        return

    def test_reclassify_local_vector(self, model_local_vector, tmp_dir):

        # Create a dummy translation matrix
        matrix = {1: 6, 2: 7, 3: 8, 4: 9, 5: 10}

        # Act
        model_local_vector.matrix = matrix
        model_local_vector.band = "BoroCode"
        model_local_vector.reclassify()

        # Assert
        dst = tmp_dir / f"{Path(model_local_vector.src_local).stem}_reclass.shp"

        assert model_local_vector.dst_local == str(dst)

        # remove the created file
        Path(model_local_vector.dst_local).unlink()

        return

    @pytest.fixture
    def reclass_file(self, tmp_dir):
        """create a fake classification file"""

        reclass_file = tmp_dir / "dum_map_matrix.csv"
        reclass_file.write_text(
            """
            1,Forest,#044D02\n
            2,Grassland,#F5FF00\n
            3,Cropland,#FF8100\n
            4,Wetland,#0013FF\n
            5,Settlement,#FFFFFF\n
            6,Other land,#FF00DE\n
        """
        )

        yield reclass_file

        # delete the file
        reclass_file.unlink()

        return

    @pytest.fixture
    def model_gee(self, tmp_dir, alert, gee_ready, gee_dir):
        """Reclassify model using Google Earth Engine assets"""

        aoi_model = aoi.AoiModel(alert, gee=True, folder=gee_dir)

        return ReclassifyModel(
            enforce_aoi=True,
            gee=True,
            dst_dir=tmp_dir,
            aoi_model=aoi_model,
            save=gee_ready,
            folder=gee_dir,
        )

    @pytest.fixture
    def model_local(self, tmp_dir, alert):
        """Reclassify model using local raster assets"""

        aoi_model = aoi.AoiModel(alert, gee=False)

        return ReclassifyModel(gee=False, dst_dir=tmp_dir, aoi_model=aoi_model)

    @pytest.fixture
    def model_gee_vector(self, model_gee, gee_dir):
        """Creates a reclassify model with a gee vector"""

        model_gee = deepcopy(model_gee)
        model_gee.src_gee = f"{gee_dir}/reclassify_table"
        model_gee.get_type()

        return model_gee

    @pytest.fixture
    def model_gee_image(self, model_gee, gee_dir):
        """Creates a reclassify model with a gee image"""

        model_gee = deepcopy(model_gee)
        model_gee.src_gee = f"{gee_dir}/reclassify_image"
        model_gee.get_type()

        return model_gee

    @pytest.fixture
    def model_local_vector(self, model_local, tmp_dir):
        """Create a reclassify model with a local vector"""

        # create the vector file
        file = Path(gpd.datasets.get_path("nybb").replace("zip:", ""))

        with ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(tmp_dir)

        model_local = deepcopy(model_local)
        model_local.src_local = tmp_dir / "nybb.shp"
        model_local.get_type()

        yield model_local

        # delete the shp files
        [f.unlink() for f in tmp_dir.glob("nybb.*")]

        return

    @pytest.fixture
    def model_local_image(self, model_local, tmp_dir):
        """create a reclassify model with a tif image"""

        # retreive the image
        url = "https://raw.githubusercontent.com/12rambau/gwb/master/utils/backup/clc3class.tif"
        filename = tmp_dir / "clc3class.tif"
        urlretrieve(url, filename)

        model_local = deepcopy(model_local)
        model_local.src_local = str(filename)
        model_local.get_type()

        yield model_local

        # delete the file
        filename.unlink()

        return
