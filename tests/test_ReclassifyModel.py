from pathlib import Path
from copy import deepcopy
import pytest

from sepal_ui.reclassify import ReclassifyModel


@pytest.fixture
def model_gee(aoi_model_gee, dum_dir):
    """Reclassify model using Google Earth Engine assets"""

    return ReclassifyModel(
        gee=True, dst_dir=dum_dir, aoi_model=aoi_model_gee, folder=dum_dir, save=True
    )


@pytest.fixture
def model_local(aoi_model_local, dum_dir):
    """Reclassify model using local raster assets"""

    return ReclassifyModel(
        gee=False, dst_dir=dum_dir, aoi_model=aoi_model_local, folder=dum_dir, save=True
    )


@pytest.fixture
def model_gee_vector(model_gee):
    """Creates a reclassify model with a gee vector"""
    # Arrange - Act
    # assign a well known VECTOR asset.
    # Input type=False to vector, True to Image
    model_gee = deepcopy(model_gee)
    model_gee.src_gee = "users/dafguerrerom/FAO/TESTS/LULC_2012_AOI"
    model_gee.input_type = False

    return model_gee


@pytest.fixture
def model_gee_image(model_gee):
    # Arrange - Act
    # assign a well known IMAGE asset
    # Input type=False to vector, True to Image
    model_gee = deepcopy(model_gee)
    model_gee.src_gee = "users/dafguerrerom/FAO/TESTS/LULC_example"
    model_gee.input_type = True

    return model_gee


@pytest.fixture
def model_local_vector(model_local, aoi_model_local):

    # Input type=False to vector, True to Image
    model_local = deepcopy(model_local)
    model_local.src_local = aoi_model_local.default_vector
    model_local.input_type = False

    return model_local


@pytest.fixture
def model_local_image(model_local):

    # Input type=False to vector, True to Image
    model_local = deepcopy(model_local)
    model_local.src_local = Path(__file__).parent / "samples/clc3class.tif"
    model_local.input_type = True

    return model_local


def test_gee_init(model_gee):

    assert model_gee.gee == True


def test_local_init(model_local):

    assert model_local.gee == False


def test_get_classes(model_gee, dum_dir):
    """Test if the matrix is saved and corresponds with the the output"""

    with pytest.raises(Exception):
        model_gee.get_classes("I/dont/exist.nothing")

    # Arrange
    reclass_file = dum_dir / "dum_map_matrix.csv"
    reclass_file.write_text(
        """1,Forest,#044D02\n
        2,Grassland,#F5FF00\n
        3,Cropland,#FF8100\n
        4,Wetland,#0013FF\n
        5,Settlement,#FFFFFF\n
        6,Other land,#FF00DE\n"""
    )

    expected_class_dict = {
        1: ("Forest", "#044D02"),
        2: ("Grassland", "#F5FF00"),
        3: ("Cropland", "#FF8100"),
        4: ("Wetland", "#0013FF"),
        5: ("Settlement", "#FFFFFF"),
        6: ("Other land", "#FF00DE"),
    }

    # Act
    class_dict = model_gee.get_classes(reclass_file)

    # Assert
    assert class_dict == expected_class_dict


def test_get_type_gee(model_gee, model_gee_vector, model_gee_image):
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


def test_get_type_local(model_local, model_local_vector, model_local_image):
    """Tests the asset type with gee"""

    # Test no input
    with pytest.raises(Exception):
        model_local.get_type()
    # Test with a local vector. Let's use the model
    assert model_local_vector.get_type() is False

    # Test with a local image
    assert model_local_image.get_type() is True


def test_get_bands_gee(model_gee_vector, model_gee_image):

    # Arrange
    table_bands = [
        "APOYO",
        "AREA_HA",
        "CAMBIO",
        "CODIGO",
        "CONFIABILI",
        "INSUMO",
        "LEYENDA3N",
        "OBJECTID",
        "OBJECTID_1",
        "OBJECTID_2",
        "RULEID",
        "Shape_Le_1",
        "Shape_Le_2",
        "Shape_Leng",
    ]

    image_bands = [
        "y1992",
        "y1993",
        "y1994",
        "y1995",
        "y1996",
        "y1997",
        "y1998",
        "y1999",
        "y2000",
        "y2001",
        "y2002",
        "y2003",
        "y2004",
        "y2005",
        "y2006",
        "y2007",
        "y2008",
        "y2009",
        "y2010",
        "y2011",
        "y2012",
        "y2013",
        "y2014",
        "y2015",
        "y2016",
        "y2017",
        "y2018",
    ]

    # Act - Assert
    assert model_gee_vector.get_bands() == table_bands
    assert model_gee_image.get_bands() == image_bands


def test_get_bands_local(model_local_vector, model_local_image):

    table_bands = ["BoroCode", "BoroName", "Shape_Area", "Shape_Leng"]
    image_bands = [1]

    assert model_local_vector.get_bands() == table_bands
    assert model_local_image.get_bands() == image_bands


def test_get_aoi(model_gee):

    assert model_gee.get_aoi() is not None

    model_gee.aoi_model.feature_collection = None

    # Test when there is an aoi but there is not a feature collection selected
    with pytest.raises(Exception):
        model_gee.get_aoi()

    # TODO: Create test when using a vector file


def test_unique_gee_image(model_gee_image):

    # Arrange

    # Unique values when not using an area of interes
    image_unique = {
        "10": ("no_name", "#000000"),
        "11": ("no_name", "#000000"),
        "30": ("no_name", "#000000"),
        "40": ("no_name", "#000000"),
        "50": ("no_name", "#000000"),
        "60": ("no_name", "#000000"),
        "100": ("no_name", "#000000"),
        "110": ("no_name", "#000000"),
        "120": ("no_name", "#000000"),
        "130": ("no_name", "#000000"),
        "150": ("no_name", "#000000"),
        "160": ("no_name", "#000000"),
        "180": ("no_name", "#000000"),
        "190": ("no_name", "#000000"),
        "210": ("no_name", "#000000"),
    }

    # Unique values when using a sample area of interest
    image_unique_aoi = {
        "11": ("no_name", "#000000"),
        "30": ("no_name", "#000000"),
        "40": ("no_name", "#000000"),
        "50": ("no_name", "#000000"),
        "100": ("no_name", "#000000"),
        "110": ("no_name", "#000000"),
        "120": ("no_name", "#000000"),
        "130": ("no_name", "#000000"),
        "180": ("no_name", "#000000"),
    }

    model_gee_image.band = "y1992"
    model_gee_image.aoi_model.set_default(
        asset="users/dafguerrerom/FAO/TESTS/LULC_example_inner_geometry"
    )
    assert model_gee_image.unique() == image_unique_aoi

    model_gee_image.aoi_model = None
    assert model_gee_image.unique() == image_unique


def test_unique_gee_vector(model_gee_vector):

    # Arrange

    # Unique values when not using an area of interest
    vector_unique = {
        111: ("no_name", "#000000"),
        112: ("no_name", "#000000"),
        231: ("no_name", "#000000"),
        232: ("no_name", "#000000"),
        233: ("no_name", "#000000"),
        242: ("no_name", "#000000"),
        243: ("no_name", "#000000"),
        244: ("no_name", "#000000"),
        245: ("no_name", "#000000"),
        313: ("no_name", "#000000"),
        314: ("no_name", "#000000"),
        323: ("no_name", "#000000"),
        333: ("no_name", "#000000"),
        334: ("no_name", "#000000"),
        511: ("no_name", "#000000"),
        512: ("no_name", "#000000"),
        1312: ("no_name", "#000000"),
        2121: ("no_name", "#000000"),
        2141: ("no_name", "#000000"),
        2232: ("no_name", "#000000"),
        3131: ("no_name", "#000000"),
        3132: ("no_name", "#000000"),
        3221: ("no_name", "#000000"),
        3222: ("no_name", "#000000"),
        3231: ("no_name", "#000000"),
        3232: ("no_name", "#000000"),
        31111: ("no_name", "#000000"),
        31121: ("no_name", "#000000"),
        31211: ("no_name", "#000000"),
        31221: ("no_name", "#000000"),
        32111: ("no_name", "#000000"),
        32112: ("no_name", "#000000"),
    }

    # Unique values when using an area of interest
    vector_unique_aoi = {
        231: ("no_name", "#000000"),
        233: ("no_name", "#000000"),
        244: ("no_name", "#000000"),
        313: ("no_name", "#000000"),
        314: ("no_name", "#000000"),
        323: ("no_name", "#000000"),
        333: ("no_name", "#000000"),
        511: ("no_name", "#000000"),
        3131: ("no_name", "#000000"),
        3132: ("no_name", "#000000"),
        31111: ("no_name", "#000000"),
        31121: ("no_name", "#000000"),
    }

    model_gee_vector.band = "CODIGO"
    model_gee_vector.aoi_model.set_default(
        asset="users/dafguerrerom/FAO/TESTS/LULC_2012_AOI_inner_gometry"
    )
    assert model_gee_vector.unique() == vector_unique_aoi

    model_gee_vector.aoi_model = None
    assert model_gee_vector.unique() == vector_unique


def test_unique_local_image(model_local_image):

    image_unique = {
        1: ("no_name", "#000000"),
        2: ("no_name", "#000000"),
        3: ("no_name", "#000000"),
    }

    model_local_image.band = 1
    assert model_local_image.unique() == image_unique

    # TODO: We have to create the method to clip the local vector/images


def test_unique_local_vector(model_local_vector):

    vector_unique = {
        1: ("no_name", "#000000"),
        2: ("no_name", "#000000"),
        3: ("no_name", "#000000"),
        4: ("no_name", "#000000"),
        5: ("no_name", "#000000"),
    }
    model_local_vector.band = "BoroCode"
    assert model_local_vector.unique() == vector_unique


def test_reclassify_initial_exceptions(model_gee):

    # Test reclassify method without matrix
    with pytest.raises(Exception):
        model_gee.reclassify()

    # Test reclassify method without band
    with pytest.raises(Exception):
        model_gee.matrix = {1: 1}
        model_gee.reclassify()


def test_reclassify_local_image(model_local_image):

    # Create a dummy translation matrix for local image
    matrix = {1: 4, 2: 5, 3: 6}

    new_unique_values = {
        4: ("no_name", "#000000"),
        5: ("no_name", "#000000"),
        6: ("no_name", "#000000"),
    }

    model_local_image.matrix = matrix
    model_local_image.band = 1
    model_local_image.reclassify()

    assert model_local_image.dst_local is not None

    # Get the unique values of the reclassified raster and assert that
    # are equal to the expected result
    model_local_image.src_local = model_local_image.dst_local

    assert new_unique_values == model_local_image.unique()


def test_reclassify_local_vector(model_local_vector):

    # Create a dummy translation matrix
    matrix = {1: 6, 2: 7, 3: 8, 4: 9, 5: 10}

    # Act
    model_local_vector.matrix = matrix
    model_local_vector.band = "BoroCode"
    model_local_vector.reclassify()

    # Assert
    assert model_local_vector.dst_local is not None

    reclassify_matrix = dict(
        zip(
            model_local_vector.dst_local_memory["BoroCode"].to_list(),
            model_local_vector.dst_local_memory["reclass"].to_list(),
        )
    )

    assert matrix == reclassify_matrix
