"""Test VectorField widget."""

from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile

import ee
import pytest

from sepal_ui import sepalwidgets as sw


def test_init() -> None:
    """Check the widget init."""
    vector_field = sw.VectorField()

    assert isinstance(vector_field, sw.VectorField)

    return


def test_update_file(fake_vector: Path, default_v_model: dict) -> None:
    """Update the selected file and check the widget behaviour.

    Args:
        fake_vector: the path to a fake vector file
        default_v_model: the default v_model values
    """
    vector_field = sw.VectorField()

    # change the value of the file
    vector_field._update_file({"new": str(fake_vector)})

    test_data = {
        "pathname": str(fake_vector),
        "column": "ALL",
        "value": None,
    }

    assert vector_field.v_model == test_data

    # change for a empty file
    vector_field._update_file({"new": None})
    assert vector_field.v_model == default_v_model

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_update_file_gee(
    gee_dir: Path, default_v_model: dict, fake_asset: Path
) -> None:
    """Update the selected file and check the widget behaviour in a GEE context.

    Args:
        gee_dir: The session created GEE directory
        fake_asset: the path to a fake vector asset
        default_v_model: the default v_model values
    """
    vector_field_gee = sw.VectorField(gee=True, folder=gee_dir)
    # Arrange
    test_data = {
        "pathname": str(fake_asset),
        "column": "ALL",
        "value": None,
    }

    # Act
    vector_field_gee._update_file({"new": str(fake_asset)})

    # Assert
    assert vector_field_gee.v_model == test_data

    vector_field_gee._update_file({"new": None})
    assert vector_field_gee.v_model == default_v_model

    return


def test_reset(fake_vector: Path, default_v_model: dict) -> None:
    """Reset an already set widget.

    Args:
        fake_vector: the path to a fake vector file
        default_v_model: the default v_model values
    """
    # trigger the event
    vector_field = sw.VectorField()
    vector_field.w_file.v_model = str(fake_vector)

    # reset the loadtable
    vector_field.reset()

    # assert the current values
    assert vector_field.v_model == default_v_model

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_reset_gee(gee_dir: Path, default_v_model: dict, fake_asset: Path) -> None:
    """Reset an already set widget in GEE context.

    Args:
        gee_dir: The session created GEE directory
        fake_asset: the path to a fake vector asset
        default_v_model: the default v_model values
    """
    # It will trigger the event
    vector_field_gee = sw.VectorField(gee=True, folder=gee_dir)
    vector_field_gee.w_file.v_model = str(fake_asset)

    # reset the loadtable
    vector_field_gee.reset()

    # assert the current values
    assert vector_field_gee.v_model == default_v_model

    return


def test_update_column(fake_vector: Path) -> None:
    """Update a single column in a vector field.

    Args:
        fake_vector: the path to a fake vector file
    """
    # change the value of the file
    vector_field = sw.VectorField()
    vector_field._update_file({"new": str(fake_vector)})

    # read a column
    vector_field.w_column.v_model = "GID_0"  # first one to select
    assert vector_field.v_model["column"] == "GID_0"
    assert "d-none" not in vector_field.w_value.class_
    assert vector_field.w_value.items == ["VAT"]

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_update_column_gee(gee_dir: Path, fake_asset: Path) -> None:
    """Update a single column in a vector field in GEE context.

    Args:
        gee_dir: The session created GEE directory
        fake_asset: the path to a fake vector asset
    """
    # change the value of the file
    vector_field_gee = sw.VectorField(gee=True, folder=gee_dir)
    vector_field_gee._update_file({"new": str(fake_asset)})

    # read a column
    vector_field_gee.w_column.v_model = "data"
    assert vector_field_gee.v_model["column"] == "data"
    assert "d-none" not in vector_field_gee.w_value.class_
    assert vector_field_gee.w_value.items == [0, 1, 2, 3]

    return


def test_update_value(fake_vector: Path) -> None:
    """Check the update of a value in an already selected column.

    Args:
        fake_vector: the path to a fake vector file
    """
    # change the value of the file
    vector_field = sw.VectorField()
    vector_field._update_file({"new": str(fake_vector)})

    # read a column
    vector_field.w_column.v_model = "GID_0"  # first one to select
    vector_field.w_value.v_model = "VAT"  # unique possible value

    assert vector_field.v_model["value"] == "VAT"

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_update_value_gee(gee_dir: Path, fake_asset: Path) -> None:
    """Check the update of a value in an already selected column in GEE context.

    Args:
        gee_dir: The session created GEE directory
        fake_asset: the path to a fake vector asset
    """
    # change the value of the file
    vector_field_gee = sw.VectorField(gee=True, folder=gee_dir)
    vector_field_gee._update_file({"new": str(fake_asset)})

    # read a column
    vector_field_gee.w_column.v_model = "data"
    vector_field_gee.w_value.v_model = 1

    assert vector_field_gee.v_model["value"] == 1

    return


@pytest.fixture
def default_v_model() -> dict:
    """Returns the default v_model.

    Returns:
        the default v_model
    """
    return {
        "pathname": None,
        "column": None,
        "value": None,
    }


@pytest.fixture
def fake_vector(tmp_dir: Path) -> Path:
    """Return a fake vector based on the vatican file.

    Args:
        tmp_dir: the session created tmp directory

    Returns:
        the path to the created file
    """
    file = tmp_dir / "test.zip"

    gadm_vat_link = "https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_VAT_shp.zip"
    name = "gadm36_VAT_0"

    # download vatican city from GADM
    urlretrieve(gadm_vat_link, file)

    with ZipFile(file, "r") as zip_ref:
        zip_ref.extractall(tmp_dir)

    file.unlink()

    yield tmp_dir / f"{name}.shp"

    # delete the files
    [f.unlink() for f in tmp_dir.glob(f"{name}.*")]

    return


@pytest.fixture
def fake_asset(gee_dir: Path) -> Path:
    """Return the path to a fake asset.

    Returns:
        the path to the dir
    """
    return gee_dir / "feature_collection"
