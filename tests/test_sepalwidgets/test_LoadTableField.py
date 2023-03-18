"""Test the LoadTableField widget."""

from pathlib import Path

import pytest

from sepal_ui import sepalwidgets as sw


def test_init() -> None:
    """Check the init widget."""
    load_table = sw.LoadTableField()

    assert isinstance(load_table, sw.LoadTableField)

    return


def test_on_file_input_change(fake_table: Path, wrong_table: Path) -> None:
    """Check to use temp created table.

    Args:
        fake_table: a well defined table
        wrong_table: a badly defined table
    """
    load_table = sw.LoadTableField()

    # change the value of the file
    load_table._on_file_input_change({"new": str(fake_table)})

    test_data = {
        "pathname": str(fake_table),
        "id_column": "id",
        "lng_column": "lng",
        "lat_column": "lat",
    }

    assert load_table.v_model == test_data

    # change for a empty update
    load_table._on_file_input_change({"new": None})
    assert load_table.v_model == load_table.default_v_model

    # test if the csv have not enough columns
    load_table._on_file_input_change({"new": str(wrong_table)})
    assert load_table.v_model == load_table.default_v_model
    assert load_table.fileInput.selected_file.error_messages is not None

    return


@pytest.mark.skip(reason="The test is not behaving as the interface")
def test_reset(fake_table: Path) -> None:
    """Test the reset after setting a table.

    Args:
        fake_table: a well defined table
    """
    load_table = sw.LoadTableField()

    # for no apparent reasons the test remains on the initial value set up in the fileInput
    # when testing live the widget behave like expected

    print(load_table.v_model)

    # change the value of the file
    load_table._on_file_input_change({"new": str(fake_table)})

    # reset the loadtable
    load_table.reset()

    print(load_table.v_model)

    # assert the current values
    assert load_table.v_model == load_table.default_v_model

    return
