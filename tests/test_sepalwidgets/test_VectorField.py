"""Test VectorField widget."""

from pathlib import Path

import ee
import pytest

from sepal_ui import sepalwidgets as sw


def test_init() -> None:
    """Check the widget init."""
    vector_field = sw.VectorField()

    assert isinstance(vector_field, sw.VectorField)

    return


def test_update_file(fake_vector: Path, data_regression) -> None:
    """Update the selected file and check the widget behaviour.

    Args:
        fake_vector: the path to a fake vector file
        data_regression: the pytest regression fixture
    """
    vector_field = sw.VectorField()

    # change the value of the file
    vector_field._update_file({"new": str(fake_vector)})

    assert vector_field.v_model["pathname"] == str(fake_vector)
    assert vector_field.v_model["column"] == "ALL"
    assert vector_field.v_model["value"] is None

    # change for a empty file
    vector_field._update_file({"new": None})
    data_regression.check(vector_field.v_model, basename="default_v_model")

    return


@pytest.mark.skipif(not ee.data.is_initialized(), reason="GEE is not set")
def test_update_file_gee(gee_dir: Path, data_regression, fake_asset: Path) -> None:
    """Update the selected file and check the widget behaviour in a GEE context.

    Args:
        gee_dir: The session created GEE directory
        fake_asset: the path to a fake vector asset
        data_regression: the pytest regression fixture
    """
    vector_field_gee = sw.VectorField(gee=True, folder=gee_dir)

    vector_field_gee._update_file({"new": str(fake_asset)})

    assert vector_field_gee.v_model["pathname"] == str(fake_asset)
    assert vector_field_gee.v_model["column"] == "ALL"
    assert vector_field_gee.v_model["value"] is None

    vector_field_gee._update_file({"new": None})
    data_regression.check(vector_field_gee.v_model, basename="default_v_model")

    return


def test_reset(fake_vector: Path, data_regression) -> None:
    """Reset an already set widget.

    Args:
        fake_vector: the path to a fake vector file
        data_regression: the pytest regression fixture
    """
    # trigger the event
    vector_field = sw.VectorField()
    vector_field.w_file.v_model = str(fake_vector)

    # reset the loadtable
    vector_field.reset()

    # assert the current values
    data_regression.check(vector_field.v_model, basename="default_v_model")

    return


@pytest.mark.skipif(not ee.data.is_initialized(), reason="GEE is not set")
def test_reset_gee(gee_dir: Path, data_regression, fake_asset: Path) -> None:
    """Reset an already set widget in GEE context.

    Args:
        gee_dir: The session created GEE directory
        fake_asset: the path to a fake vector asset
        data_regression: the pytest regression fixture
    """
    # It will trigger the event
    vector_field_gee = sw.VectorField(gee=True, folder=gee_dir)
    vector_field_gee.w_file.v_model = str(fake_asset)

    # reset the loadtable
    vector_field_gee.reset()

    # assert the current values
    data_regression.check(vector_field_gee.v_model, basename="default_v_model")

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


@pytest.mark.skipif(not ee.data.is_initialized(), reason="GEE is not set")
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


@pytest.mark.skipif(not ee.data.is_initialized(), reason="GEE is not set")
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
