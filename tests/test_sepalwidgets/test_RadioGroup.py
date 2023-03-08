"""Test the RadioGroup Widget."""

import pytest

from sepal_ui import sepalwidgets as sw


def test_init() -> None:
    """Init a RadioGroup."""
    radios = [sw.Radio(active=None, value=i) for i in range(3)]
    group = sw.RadioGroup(v_model=None, children=radios)

    assert isinstance(group, sw.RadioGroup)

    return


def test_update_radios(group: sw.RadioGroup) -> None:
    """Check that updating the radio status update the group v_model.

    Args:
        group: a RadioGRoup object
    """
    group.v_model = 1
    assert group.children[0].active is False
    assert group.children[1].active is True
    assert group.children[2].active is False

    return


def test_update_v_model(group: sw.RadioGroup) -> None:
    """Check that updating the v_model update the radio status.

    Args:
        group: a RadioGRoup object
    """
    group.children[2].active = True
    assert group.v_model == 2
    assert group.children[0].active is False
    assert group.children[1].active is False

    return


@pytest.fixture
def group() -> sw.RadioGroup:
    """Return a Radiogroup with 3 radios children.

    Returns:
        The RadioGroup object
    """
    radios = [sw.Radio(active=None, value=i) for i in range(3)]
    return sw.RadioGroup(v_model=None, children=radios)
