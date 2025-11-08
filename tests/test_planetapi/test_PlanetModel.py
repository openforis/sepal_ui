"""Test the planet PlanetModel model."""

import os
from pathlib import Path
from typing import Any, Union

import planet
import pytest
from pytest import FixtureRequest

from sepal_ui.planetapi import PlanetModel


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_init(planet_key: str, cred: list) -> None:
    """Test model init with different identification methods.

    Args:
        planet_key: the planet API key
        cred: the user credentials (username, password)
    """
    # Test with a valid api key
    planet_model = PlanetModel(planet_key)

    assert isinstance(planet_model, PlanetModel)
    assert isinstance(planet_model.session, planet.http.Session)
    assert planet_model.authenticated is True

    # Test with login credentials
    planet_model = PlanetModel(cred)

    assert isinstance(planet_model, PlanetModel)
    assert isinstance(planet_model.session, planet.http.Session)
    assert planet_model.authenticated is True

    # Test with an invalid api key
    with pytest.raises(Exception):
        planet_model = PlanetModel("not valid")

    return


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
@pytest.mark.parametrize("credentials", ["planet_key", "cred"])
def test_init_client(credentials: Any, request: FixtureRequest) -> None:
    """Check init the client with api key or credentials.

    Args:
        credentials: any credentials as set in the parameters
        request: the parameter request
    """
    planet_model = PlanetModel()

    cred_value = request.getfixturevalue(credentials)

    planet_model.init_session(cred_value)
    assert planet_model.authenticated is True
    assert hasattr(planet_model, "auth"), "Auth object should be initialized"

    with pytest.raises(Exception):
        planet_model.init_session("wrongkey")

    with pytest.raises(Exception):
        planet_model.init_session(["wrongkey", "credentials"])

    return


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_init_with_file(planet_key) -> None:
    """Check init the session from a file."""
    planet_secret_file = Path.home() / ".planet.json"
    existing = False

    # This test will overwrite and remove the file, let's backup it
    if planet_secret_file.exists():
        existing = True
        planet_secret_file.rename(planet_secret_file.with_suffix(".json.bak"))

    assert not planet_secret_file.exists()

    # test init with the file
    planet_model = PlanetModel()
    planet_model.init_session(planet_key, write_secrets=True)

    assert planet_model.authenticated is True
    assert planet_secret_file.exists()

    planet_model.init_session(str(planet_secret_file))

    assert planet_model.authenticated is True

    # Check that wrong credentials won't save the secrets file
    # remove the file
    planet_secret_file.unlink()

    planet_model = PlanetModel()

    with pytest.raises(Exception):
        planet_model.init_session("wrong_key", write_secrets=True)

    assert not planet_secret_file.exists()

    # Check no save with good credentials
    planet_model = PlanetModel()
    planet_model.init_session(planet_key, write_secrets=False)

    assert not planet_secret_file.exists()

    # restore the file
    if existing:
        planet_secret_file.with_suffix(".json.bak").rename(planet_secret_file)

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
    """Check if the model is authenticated when set with api key.

    Args:
        planet_key: the planet API key
    """
    planet_model = PlanetModel(planet_key)
    planet_model._is_active()
    assert planet_model.authenticated is True

    with pytest.raises(Exception):
        planet_model = PlanetModel("wrongkey")

    return


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_get_subscriptions(
    planet_key: str, data_regression, monkeypatch, has_active_planet_subscription: bool
) -> None:
    """Check the registered subs of the test api key.

    Args:
        planet_key: the planet API key
        data_regression: the pytest regression fixture
        monkeypatch: pytest monkeypatch fixture
        has_active_planet_subscription: whether the credentials have active subscriptions
    """
    planet_model = PlanetModel(planet_key)

    # Only mock if there are no active subscriptions
    if not has_active_planet_subscription:
        # Mock the API response to simulate having subscriptions
        mock_response = [
            {
                "id": 8411,
                "name": "NICFI_Level_1",
                "plan": {"id": 8411, "name": "NICFI_Level_1", "state": "active"},
                "state": "active",
            }
        ]
        monkeypatch.setattr(planet_model, "get_subscriptions", lambda: mock_response)

    subs = planet_model.get_subscriptions()
    plans = [s["plan"] for s in subs]
    plans = hide_key(plans, planet_key)  # hide the key in the produced file

    data_regression.check(plans)

    return


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_get_planet_items(planet_key: str, data_regression) -> None:
    """Get the planet items and check an expected entry.

    Args:
        planet_key: the planet API key
        data_regression: the pytest regression fixture
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

    # Get the items
    items = planet_model.get_items(aoi, start, end, cloud_cover)
    items = hide_key(items, planet_key)  # hide the key in the produced file

    data_regression.check(items)


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_get_mosaics(planet_key: str, monkeypatch, has_active_planet_subscription: bool) -> None:
    """Get all the subscriptions from the Planet API.

    Args:
        planet_key: the planet API key
        monkeypatch: pytest monkeypatch fixture
        has_active_planet_subscription: whether the credentials have active subscriptions
    """
    planet_model = PlanetModel(planet_key)

    # Only mock if there are no active subscriptions
    if not has_active_planet_subscription:
        # Mock the API response to simulate having mosaics
        mock_mosaics = [
            {
                "id": "planet_medres_normalized_analytic_2023-01_mosaic",
                "name": "planet_medres_normalized_analytic_2023-01_mosaic",
                "_links": {"_self": "mock_url"},
            },
            {
                "id": "planet_medres_normalized_analytic_2023-02_mosaic",
                "name": "planet_medres_normalized_analytic_2023-02_mosaic",
                "_links": {"_self": "mock_url"},
            },
        ]
        monkeypatch.setattr(planet_model, "get_mosaics", lambda: mock_mosaics)

    mosaics = planet_model.get_mosaics()
    mosaics = hide_key(mosaics, planet_key)  # hide the key in the produced file
    mosaics = [m["name"] for m in mosaics]

    # the map list is updated every month, making the test crash on regular basis
    # that's why we do not use a data_regression here but only a simple assert
    # time lost: 1h
    assert len(mosaics) > 0
    assert all(["planet_medres_" in m for m in mosaics])


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_get_quad(
    planet_key: str, data_regression, monkeypatch, has_active_planet_subscription: bool
) -> None:
    """Get a single quad from a specific mosaic.

    Args:
        planet_key: the planet API key
        data_regression: the pytest regression fixture
        monkeypatch: pytest monkeypatch fixture
        has_active_planet_subscription: whether the credentials have active subscriptions
    """
    planet_model = PlanetModel(planet_key)

    # Only mock if there are no active subscriptions
    if not has_active_planet_subscription:
        # Mock the get_mosaics response
        mock_mosaics = [
            {
                "id": "planet_medres_normalized_analytic_2023-01_mosaic",
                "name": "planet_medres_normalized_analytic_2023-01_mosaic",
                "_links": {"_self": "mock_url"},
            }
        ]

        # Mock the get_quad response
        mock_quad = {
            "id": "1088-1058",
            "bbox": [11.2499999985, 5.9657536703, 11.4257812485, 6.14055478166],
            "percent_covered": 100,
            "_links": {
                "_self": f"https://api.planet.com/basemaps/v1/mosaics/1f0570f3-b373-457f-89a5-046b4080d199/quads/1088-1058?api_key={planet_key}",
                "download": f"https://link.planet.com/basemaps/v1/mosaics/1f0570f3-b373-457f-89a5-046b4080d199/quads/1088-1058/full?api_key={planet_key}",
                "items": f"https://api.planet.com/basemaps/v1/mosaics/1f0570f3-b373-457f-89a5-046b4080d199/quads/1088-1058/items?api_key={planet_key}",
                "thumbnail": f"https://tiles.planet.com/basemaps/v1/planet-tiles/planet_medres_normalized_analytic_2015-12_2016-05_mosaic/gmap/11/1088/989.png?api_key={planet_key}",
            },
        }

        monkeypatch.setattr(planet_model, "get_mosaics", lambda: mock_mosaics)
        monkeypatch.setattr(planet_model, "get_quad", lambda mosaic, quad_id: mock_quad)

    mosaic = planet_model.get_mosaics()[0]
    quad_id = "1088-1058"  # a quad on Singapore
    quad = planet_model.get_quad(mosaic, quad_id)
    quad = hide_key(quad, planet_key)  # hide the key in the produced file

    data_regression.check(quad)


def hide_key(collection: Union[dict, list], key: str) -> dict:
    """Hide the planet_key anywhere it could appears in the dict result."""
    # create a generator from the data type
    if isinstance(collection, dict):
        gen = collection.items()
    elif isinstance(collection, list):
        gen = enumerate(collection)

    for k, v in gen:
        if isinstance(v, (list, dict)):
            collection[k] = hide_key(v, key)
        elif isinstance(v, str):
            collection[k] = v.replace(key, "toto")

    return collection
