"""Test PlanetView widget."""

import json
import os

import pytest

from sepal_ui import sepalwidgets as sw
from sepal_ui.planetapi import PlanetView


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_init() -> None:
    """Check the widget init."""
    planet_view = PlanetView()

    # check the feault planet_view
    assert isinstance(planet_view, PlanetView)

    # With external components
    external_btn = sw.Btn()
    external_alert = sw.Btn()
    planet_view = PlanetView(btn=external_btn, alert=external_alert)

    assert planet_view.btn == external_btn
    assert planet_view.alert == external_alert

    return


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_reset() -> None:
    """Check the widget can be reset."""
    planet_view = PlanetView()

    # add dummy parameter
    planet_view.w_username.v_model = "dummy"
    planet_view.w_password.v_model = "dummy"
    planet_view.w_key.v_model = "dummy"

    # reset the view
    planet_view.reset()
    assert planet_view.w_username.v_model is None
    assert planet_view.w_password.v_model is None
    assert planet_view.w_key.v_model is None

    # use a default method
    default_method = "credentials"
    assert planet_view.w_method.v_model == default_method
    assert planet_view.w_username.viz is True
    assert planet_view.w_password.viz is True
    assert planet_view.w_key.viz is False

    # change the method
    planet_view.w_method.v_model = "api_key"
    assert planet_view.w_method.v_model == "api_key"
    assert planet_view.w_username.viz is False
    assert planet_view.w_password.viz is False
    assert planet_view.w_key.viz is True

    return


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_validate() -> None:
    """Check the probvided credentials can be validated."""
    planet_view = PlanetView()

    # Arrange
    credentials = tuple(json.loads(os.getenv("PLANET_API_CREDENTIALS")).values())
    api_key = os.getenv("PLANET_API_KEY")

    # Act with credentials
    planet_view.w_method.v_model = "credentials"
    planet_view.w_username.v_model, planet_view.w_password.v_model = credentials
    planet_view.btn.fire_event("click", None)
    assert planet_view.planet_model.active is True

    # Act with api_key
    planet_view.w_method.v_model = "api_key"
    planet_view.w_key.v_model = api_key
    planet_view.btn.fire_event("click", None)
    assert planet_view.planet_model.active is True

    return
