"""Test the PlanetWidget widget."""

import pytest

from sepal_ui.planetapi import PlanetModel
from sepal_ui.planetapi.planet_widgets import InfoView


def test_init() -> None:
    """Check widget init."""
    info_view = InfoView(model=PlanetModel())

    assert isinstance(info_view, InfoView)

    return


def test_open_info(plan: dict) -> None:
    """Check the display of subs in different configurations.

    Args:
        plan: the structure of a plan to check display update
    """
    info_view = InfoView(model=PlanetModel())

    nicfi_sub = info_view.get_children(attr="id", value="nicfi")[0]
    other_sub = info_view.get_children(attr="id", value="others")[0]

    # Trigger event to check subscriptions
    info_view.model.subscriptions = {}
    info_view.model.subscriptions = {"nicfi": [], "others": []}
    assert nicfi_sub.disabled is True
    assert other_sub.disabled is True

    info_view.model.subscriptions = {}
    info_view.model.subscriptions = {"nicfi": [], "others": [plan]}
    assert nicfi_sub.disabled is True
    assert other_sub.disabled is False

    info_view.model.subscriptions = {}
    info_view.model.subscriptions = {"nicfi": [plan], "others": []}
    assert nicfi_sub.disabled is False
    assert other_sub.disabled is True

    info_view.model.subscriptions = {}
    info_view.model.subscriptions = {"nicfi": [plan], "others": [plan]}
    assert nicfi_sub.disabled is False
    assert other_sub.disabled is False

    # Check the info displayed in the cards
    assert info_view.v_model == 1
    nicfi_sub.fire_event("click", None)
    assert len(info_view.info_card.children) == 1
    assert (
        info_view.info_card.children[0].children[0].children[0] == plan["plan"]["name"]
    )
    assert info_view.v_model == 0

    # If we click the button two times, it will close the expansion panel
    nicfi_sub.fire_event("click", None)
    assert info_view.v_model == 1

    return


@pytest.fixture
def plan() -> dict:
    """A plan dict."""
    return {
        "plan": {
            "name": "level0",
            "state": "active",
        },
        "active_from": "2022-03-04T02:28:03.053172+00:00",
        "active_to": "2022-05-04T02:28:03.053172+00:00",
    }
