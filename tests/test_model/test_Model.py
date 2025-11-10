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

    assert str(dum_model) == 'DummyClass(dummy1="test1", dummy2="test2")'

    return


def test_repr_with_different_types(dum_model: DummyClass) -> None:
    """Check the representation of a model with different data types.

    Args:
        dum_model: a dummy model
    """
    # Test with strings - should use double quotes
    dum_model.dummy1 = "test_string"
    dum_model.dummy2 = "another_string"
    assert str(dum_model) == 'DummyClass(dummy1="test_string", dummy2="another_string")'

    # Test with integers - should use repr()
    dum_model.dummy1 = 42
    dum_model.dummy2 = 100
    assert str(dum_model) == "DummyClass(dummy1=42, dummy2=100)"

    # Test with floats - should use repr()
    dum_model.dummy1 = 3.14
    dum_model.dummy2 = 2.71
    assert str(dum_model) == "DummyClass(dummy1=3.14, dummy2=2.71)"

    # Test with lists - should use repr()
    dum_model.dummy1 = [1, 2, 3]
    dum_model.dummy2 = ["a", "b"]
    assert str(dum_model) == "DummyClass(dummy1=[1, 2, 3], dummy2=['a', 'b'])"

    # Test with dicts - should use repr()
    dum_model.dummy1 = {"key": "value"}
    dum_model.dummy2 = {"num": 123}
    assert str(dum_model) == "DummyClass(dummy1={'key': 'value'}, dummy2={'num': 123})"

    # Test with None - should use repr()
    dum_model.dummy1 = None
    dum_model.dummy2 = None
    assert str(dum_model) == "DummyClass(dummy1=None, dummy2=None)"

    # Test with booleans - should use repr()
    dum_model.dummy1 = True
    dum_model.dummy2 = False
    assert str(dum_model) == "DummyClass(dummy1=True, dummy2=False)"

    # Test with mixed types
    dum_model.dummy1 = "string_value"
    dum_model.dummy2 = 42
    assert str(dum_model) == 'DummyClass(dummy1="string_value", dummy2=42)'

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
