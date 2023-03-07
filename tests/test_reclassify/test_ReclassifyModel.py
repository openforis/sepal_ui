"""Test the ReclassifyModel widget"""

from copy import deepcopy
from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile

import ee
import geopandas as gpd
import pytest

from sepal_ui import aoi
from sepal_ui.reclassify import ReclassifyModel


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_gee_init(model_gee):
    """Test will eventually be removed"""
    assert isinstance(model_gee, ReclassifyModel)
    assert model_gee.gee is True

    return


def test_local_init(model_local):
    """Test will eventually be removed"""
    assert isinstance(model_local, ReclassifyModel)
    assert model_local.gee is False

    return


def test_get_classes(model_local, reclass_file):
    """Test if the matrix is saved and corresponds with the the output."""
    with pytest.raises(Exception):
        model_local.dst_class_file = "I/dont/exist.nothing"
        model_local.get_classes()

    # test these class
    expected_class_dict = {
        1: ("Forest", "#044D02"),
        2: ("Grassland", "#F5FF00"),
        3: ("Cropland", "#FF8100"),
        4: ("Wetland", "#0013FF"),
        5: ("Settlement", "#FFFFFF"),
        6: ("Other land", "#FF00DE"),
    }

    # load the class file
    model_local.dst_class_file = str(reclass_file)
    class_dict = model_local.get_classes()
    assert class_dict == expected_class_dict

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_get_type_gee(model_gee, model_gee_vector, model_gee_image):
    """Tests the asset type with gee."""
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


def test_get_type_local(model_local, model_local_vector, model_local_image):
    """Tests the asset type without gee."""
    # Test no input
    with pytest.raises(Exception):
        model_local.get_type()

    # Test with a local vector. Let's use the model
    assert model_local_vector.get_type() is False

    # Test with a local image
    assert model_local_image.get_type() is True

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_get_bands_gee(model_gee_vector, model_gee_image):
    """check if the bands are correctly retreived."""
    # Arrange
    table_bands = ["data"]
    image_bands = ["constant"]

    # assert
    assert model_gee_vector.get_bands() == table_bands
    assert model_gee_image.get_bands() == image_bands

    return


def test_get_bands_local(model_local_vector, model_local_image):
    """Test will eventually be removed"""
    table_bands = ["BoroCode", "BoroName", "Shape_Area", "Shape_Leng"]
    image_bands = [1]

    assert model_local_vector.get_bands() == table_bands
    assert model_local_image.get_bands() == image_bands

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_get_aoi(model_gee):
    """Test will eventually be removed"""
    # tested on model_gee instead of model_local a clipping is not yet
    # possible on local gdf and/or raster

    # default to error if no asset is set in the aoi_model
    with pytest.raises(Exception):
        model_gee.enforce_aoi = True
        assert model_gee.get_aoi() is None

    # Test when there is an aoi but there is not a feature collection selected
    model_gee.enforce_aoi = False
    assert model_gee.get_aoi() is None

    # set the aoi to france
    model_gee.aoi_model._from_admin("110")  # Vatican city
    assert model_gee.get_aoi() is not None

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_unique_gee_image(model_gee_image, aoi_model, no_name):
    """Test will eventually be removed"""
    # read the band of the image
    model_gee_image.band = "constant"

    # Unique values when using a sample area of interest
    image_unique_aoi = [2]
    model_gee_image.aoi_model = aoi_model
    assert model_gee_image.get_aoi() is not None
    assert model_gee_image.unique() == {str(i): no_name for i in image_unique_aoi}

    # unique value when no aoi is set
    # tested after as we delete the aoi_model
    image_unique = [1, 2, 3, 4]
    model_gee_image.aoi_model = None
    assert model_gee_image.unique() == {str(i): no_name for i in image_unique}

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_unique_gee_vector(model_gee_vector, aoi_model, no_name):
    """Test will eventually be removed"""
    model_gee_vector.band = "data"

    # Unique values when using an area of interest
    vector_unique_aoi = [3]
    model_gee_vector.aoi_model = aoi_model
    assert model_gee_vector.get_aoi() is not None
    assert model_gee_vector.unique() == {i: no_name for i in vector_unique_aoi}

    # Unique values when not using an area of interest
    # tested after as we delete the aoi_model
    vector_unique = [0, 1, 2, 3]
    model_gee_vector.aoi_model = None
    model_gee_vector.band = "data"
    assert model_gee_vector.unique() == {i: no_name for i in vector_unique}

    return


def test_unique_local_image(model_local_image, no_name):
    """Test will eventually be removed"""
    image_unique = [1, 2, 3]

    model_local_image.band = 1
    assert model_local_image.unique() == {i: no_name for i in image_unique}

    # TODO: We have to create the method to clip the local vector/images

    return


def test_unique_local_vector(model_local_vector, no_name):
    """Test will eventually be removed"""
    vector_unique = [1, 2, 3, 4, 5]

    model_local_vector.band = "BoroCode"
    assert model_local_vector.unique() == {i: no_name for i in vector_unique}

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_reclassify_initial_exceptions(model_gee_image):
    """Test will eventually be removed"""
    # Test reclassify method without matrix
    with pytest.raises(Exception):
        model_gee_image.reclassify()

    # Test reclassify method without band
    with pytest.raises(Exception):
        model_gee_image.matrix = {1: 1}
        model_gee_image.reclassify()

    # test reclassify without setting an aoi
    with pytest.raises(Exception):
        model_gee_image.enforce_aoi = True
        model_gee_image.matrix = {1: 1}
        model_gee_image.band = "constant"
        model_gee_image.reclassify()

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_reclassify_gee_vector(model_gee_vector):
    """Test reclassification of vectors when using an area of interest."""
    unique_value = [0, 1, 2, 3]
    matrix = {v: 2 * i // len(unique_value) for i, v in enumerate(unique_value)}

    model_gee_vector.matrix = matrix
    model_gee_vector.band = "data"
    model_gee_vector.reclassify()

    assert model_gee_vector.dst_gee_memory is not None

    return


def test_reclassify_gee_image(model_gee_image):
    """Test reclassification of vectors when using an area of interest."""
    unique_value = [1, 2, 3, 4]
    matrix = {v: 2 * i // len(unique_value) for i, v in enumerate(unique_value)}

    model_gee_image.matrix = matrix
    model_gee_image.band = "constant"
    model_gee_image.reclassify()

    assert model_gee_image.dst_gee_memory is not None

    return


def test_reclassify_local_image(model_local_image, tmp_dir):
    """Test will eventually be removed"""
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


def test_reclassify_local_vector(model_local_vector, tmp_dir):
    """Test will eventually be removed"""
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


@pytest.fixture(scope="class")
def reclass_file(tmp_dir):
    """create a fake classification file."""
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
def model_gee(tmp_dir, gee_dir):
    """Reclassify model using Google Earth Engine assets."""
    aoi_model = aoi.AoiModel(gee=True, folder=gee_dir)

    return ReclassifyModel(
        enforce_aoi=False,
        gee=True,
        dst_dir=tmp_dir,
        aoi_model=aoi_model,
        save=False,
        folder=gee_dir,
    )


@pytest.fixture
def model_gee_vector(model_gee, gee_dir):
    """Creates a reclassify model with a gee vector."""
    model_gee = deepcopy(model_gee)
    model_gee.src_gee = str(gee_dir / "feature_collection")
    model_gee.get_type()

    return model_gee


@pytest.fixture
def model_gee_image(model_gee, gee_dir):
    """Creates a reclassify model with a gee image."""
    model_gee = deepcopy(model_gee)
    model_gee.src_gee = str(gee_dir / "image")
    model_gee.get_type()

    return model_gee


@pytest.fixture
def model_local(tmp_dir):
    """Reclassify model using local raster assets."""
    aoi_model = aoi.AoiModel(gee=False)

    return ReclassifyModel(gee=False, dst_dir=tmp_dir, aoi_model=aoi_model)


@pytest.fixture
def model_local_vector(model_local, tmp_dir):
    """Create a reclassify model with a local vector."""
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
def model_local_image(model_local, tmp_dir):
    """create a reclassify model with a tif image."""
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


@pytest.fixture
def no_name():
    """return a no-name tuple."""
    return ("no_name", "#000000")


@pytest.fixture(scope="class")
def aoi_model(_hash, gee_dir):
    """create an aoi_model with a 100m square geometry centered in 50, 50."""
    # create the geoemtry as featurecollection
    point = ee.Geometry.Point([50, 50], "EPSG:3857")
    aoi_ee = ee.FeatureCollection(point.buffer(50).bounds())
    aoi_gdf = gpd.GeoDataFrame.from_features(aoi_ee.getInfo())

    # add it to a aoi_model
    aoi_model = aoi.AoiModel(gee=True, folder=gee_dir)
    aoi_model.feature_collection = aoi_ee
    aoi_model.gdf = aoi_gdf
    aoi_model.name = f"test_{_hash}"

    return aoi_model
