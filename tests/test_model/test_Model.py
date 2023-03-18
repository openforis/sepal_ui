"""Test the Model class."""

import json

import pytest
from traitlets import Any

from sepal_ui import model


class DummyClass(model.Model):
    """A dummy model with 2 traits, dummy1 and dummy2."""

    dummy1 = Any(None).tag(sync=True)
    dummy2 = Any(None).tag(sync=True)


def test_export(dum_model: DummyClass, test_data: dict) -> None:
    """Export model data and check validity.

    Args:
        dum_model: a dummy model
        test_data: an exportation dict of a dummy model
    """
    # create a fake model class with 2 traits
    dum_model.dummy1 = test_data["dummy1"]
    dum_model.dummy2 = test_data["dummy2"]

    dict_ = dum_model.export_data()

    # assert the result
    assert dict_ == test_data

    return


def test_import(dum_model: DummyClass, test_data: dict) -> None:
    """Check we can import data from a exported dict.

    Args:
        dum_model: a dummy model
        test_data: an exportation dict of a dummy model
    """
    # create a fake model class with 2 traits
    dum_model.import_data(test_data)

    # assert the result
    assert dum_model.dummy1 == test_data["dummy1"]
    assert dum_model.dummy2 == test_data["dummy2"]

    # create a fake model class using a str
    dum_model.import_data(json.dumps(test_data))

    # assert the result
    assert dum_model.dummy1 == test_data["dummy1"]
    assert dum_model.dummy2 == test_data["dummy2"]

    return


def test_str(dum_model: DummyClass, test_data: dict) -> None:
    """Check the representation of a model.

    Args:
        dum_model: a dummy model
        test_data: an exportation dict of a dummy model
    """
    # create a fake model class with 2 traits
    dum_model.import_data(test_data)

    assert str(dum_model) == "DummyClass(dummy1=test1, dummy2=test2)"

    return


@pytest.fixture(scope="module")
def test_data() -> dict:
    """Test data to fill a model class.

    Returns:
        traits as key value pairs
    """
    return {"dummy1": "test1", "dummy2": "test2"}


@pytest.fixture(scope="function")
def dum_model() -> DummyClass:
    """A dummyclass instance.

    Returns:
        the object
    """
    return DummyClass()
