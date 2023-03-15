"""Test the planet PlanetModel model."""

import os

import planet
import pytest
from pytest import FixtureRequest
from typing_extensions import Any

from sepal_ui.planetapi import PlanetModel


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_init(planet_key: str, cred: list) -> None:
    """Test model init with different identification methods.

    Args:
        planet_key: the planet API key
        cred: the user credentials (usernam, pasword)
    """
    # Test with a valid api key
    planet_model = PlanetModel(planet_key)

    assert isinstance(planet_model, PlanetModel)
    assert isinstance(planet_model.session, planet.http.Session)
    assert planet_model.active is True

    # Test with a valid login credentials
    planet_model = PlanetModel(cred)

    assert isinstance(planet_model, PlanetModel)
    assert isinstance(planet_model.session, planet.http.Session)
    assert planet_model.active is True

    # Test with an invalid api key
    with pytest.raises(Exception):
        planet_model = PlanetModel("not valid")

    return


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
@pytest.mark.parametrize("credentials", ["planet_key", "cred"])
def test_init_client(credentials: Any, request: FixtureRequest) -> None:
    """Check init the client with 2 methods.

    Args:
        credentials: any credentials as set in the parameters
        request: the parameter request
    """
    planet_model = PlanetModel()

    planet_model.init_session(request.getfixturevalue(credentials))
    assert planet_model.active is True

    with pytest.raises(Exception):
        planet_model.init_session("wrongkey")

    return


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_init_session_from_event() -> None:
    """Check init the session from an event."""
    planet_model = PlanetModel()

    # Test with bad credentials format
    with pytest.raises(planet.exceptions.APIError):
        planet_model.init_session(["asdf", "1234"])

    # Test with empty credentials
    with pytest.raises(ValueError):
        planet_model.init_session("")

    # Test with valid credentials format, but non real
    with pytest.raises(planet.exceptions.APIError):
        planet_model.init_session(["valid@email.format", "not_exists"])

    return


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_is_active(planet_key: str) -> None:
    """Check if the model is active when set with api key.

    Args:
        planet_key: the planet API key
    """
    planet_model = PlanetModel(planet_key)
    planet_model._is_active()
    assert planet_model.active is True

    with pytest.raises(Exception):
        planet_model = PlanetModel("wrongkey")

    return


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_get_subscriptions(planet_key: str) -> None:
    """Check the registered subs of the test api key.

    Args:
        planet_key: the planet API key
    """
    planet_model = PlanetModel(planet_key)
    subs = planet_model.get_subscriptions()

    # Check object has length, because there is no way to check a value
    # that might change over the time.
    assert len(subs) != 0

    return


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_get_planet_items(planet_key: str) -> None:
    """Get the planet items and check an expected entry.

    Args:
        planet_key: the planet API key
    """
    planet_model = PlanetModel(planet_key)
    aoi = {  # Yasuni national park in Ecuador
        "type": "Polygon",
        "coordinates": (
            (
                (-75.88994979858398, -1.442146588951299),
                (-75.9041976928711, -1.4579343782400327),
                (-75.88651657104492, -1.476982541739627),
                (-75.85647583007812, -1.4534726228737347),
                (-75.88994979858398, -1.442146588951299),
            ),
        ),
    }

    start = "2020-11-18"
    end = "2020-11-19"
    cloud_cover = 0.5

    expected_first_id = "20201118_144642_48_2262"

    # Get the items
    items = planet_model.get_items(aoi, start, end, cloud_cover)
    assert items[0].get("id") == expected_first_id
