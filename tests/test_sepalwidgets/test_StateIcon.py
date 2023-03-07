"""Test the StateIcon widget."""

import pytest
from traitlets import Unicode

import sepal_ui.sepalwidgets as sw
from sepal_ui import color
from sepal_ui.model import Model


class TestModel(Model):
    """Test model class with one single trait."""

    state_value = Unicode().tag(sync=True)


def test_init(model: TestModel) -> None:
    """Check init the widget.

    Args:
        model: the model to pilote the stateicon
    """
    # Test with default states
    state_icon = sw.StateIcon(model, "state_value")

    assert state_icon.icon.color == color.success
    assert state_icon.children[0] == "Valid"

    # Test with custom states
    custom_states = {
        "off": ("Non connected", color.darker),
        "init": ("Initializing...", color.warning),
        "failed": ("Connection failed!", color.error),
        "successfull": ("Successfull", color.success),
    }
    state_icon = sw.StateIcon(model, "state_value", custom_states)

    assert state_icon.icon.color == color.darker
    assert state_icon.children[0] == "Non connected"


def test_swap(model: TestModel) -> None:
    """Check we can swap the state of the stateicon.

    Args:
        model: the model to pilote the stateicon
    """
    state_icon = sw.StateIcon(model, "state_value")
    model.state_value = "non_valid"

    assert state_icon.icon.color == color.error
    assert state_icon.children[0] == "Not valid"

    # Test raise exception
    with pytest.raises(ValueError):
        model.state_value = "asdf"


@pytest.fixture
def model() -> TestModel:
    """Dummy model with state value trait.

    Returns:
        a test model instance
    """
    return TestModel()
