import json
import os

import pytest
from sepal_ui import sepalwidgets as sw
from sepal_ui.planetapi import PlanetView


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
class TestPlanetView:
    def test_init(self):

        # With own components
        planet_view = PlanetView()

        assert isinstance(planet_view, PlanetView)

        # With external components
        external_btn = sw.Btn()
        external_alert = sw.Btn()

        planet_view = PlanetView(btn=external_btn, alert=external_alert)

        assert planet_view.btn == external_btn
        assert planet_view.alert == external_alert

    def test_reset(self):

        # Arrange
        planet_view = PlanetView()

        planet_view.w_username.v_model = "dummy"
        planet_view.w_password.v_model = "dummy"
        planet_view.w_key.v_model = "dummy"

        # Act
        planet_view.reset()

        # Assert
        planet_view.w_username.v_model is None
        planet_view.w_password.v_model is None
        planet_view.w_key.v_model is None

    def test_swap(self):

        # Arramge
        planet_view = PlanetView()

        default_method = "credentials"

        # Assert default
        assert planet_view.w_method.v_model == default_method
        assert planet_view.w_username.viz is True
        assert planet_view.w_password.viz is True
        assert planet_view.w_key.viz is False

        # Act changing method

        planet_view.w_method.v_model = "api_key"

        # Assert change
        assert planet_view.w_method.v_model == "api_key"
        assert planet_view.w_username.viz is False
        assert planet_view.w_password.viz is False
        assert planet_view.w_key.viz is True

    def test_validate(self):

        # Arrange
        credentials = tuple(json.loads(os.getenv("PLANET_API_CREDENTIALS")).values())
        api_key = os.getenv("PLANET_API_KEY")
        planet_view = PlanetView()

        # Act with credentials
        planet_view.w_method.v_model = "credentials"
        planet_view.w_username.v_model, planet_view.w_password.v_model = credentials
        planet_view.btn.fire_event("click", None)

        # Assert
        assert planet_view.planet_model.active is True

        # Act with api_key
        planet_view.w_method.v_model = "api_key"
        planet_view.w_key.v_model = api_key
        planet_view.btn.fire_event("click", None)

        assert planet_view.planet_model.active is True
