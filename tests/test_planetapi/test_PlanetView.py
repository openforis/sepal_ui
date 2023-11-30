"""Test PlanetView widget."""

import json
import os
from pathlib import Path

import pytest

from sepal_ui import sepalwidgets as sw
from sepal_ui.message import ms
from sepal_ui.planetapi import PlanetModel, PlanetView


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
    assert planet_view.w_username.v_model == ""
    assert planet_view.w_password.v_model == ""
    assert planet_view.w_key.v_model == ""

    # use a default method
    # Default method will be from_file if the secrets file exists
    default_method = (
        "from_file" if (Path.home() / ".planet.json").exists() else "credentials"
    )
    if default_method == "credentials":
        assert planet_view.w_method.v_model == default_method
        assert planet_view.w_username.viz is True
        assert planet_view.w_password.viz is True
        assert planet_view.w_key.viz is False
        assert planet_view.w_secret_file.viz is False
    else:
        assert planet_view.w_method.v_model == default_method
        assert planet_view.w_username.viz is False
        assert planet_view.w_password.viz is False
        assert planet_view.w_key.viz is False
        assert planet_view.w_secret_file.viz is True

    # change the method
    planet_view.w_method.v_model = "api_key"
    assert planet_view.w_method.v_model == "api_key"
    assert planet_view.w_username.viz is False
    assert planet_view.w_password.viz is False
    assert planet_view.w_key.viz is True
    assert planet_view.w_secret_file.viz is False

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


@pytest.mark.skipif("PLANET_API_KEY" not in os.environ, reason="requires Planet")
def test_validate_secret_file(planet_key) -> None:
    """Test validation view method of the secret file."""
    # Arrange
    planet_secret_file = Path.home() / ".planet.json"

    # Test with existing file
    # Create a secrets file
    planet_model = PlanetModel()
    planet_model.init_session(planet_key, write_secrets=True)

    planet_view = PlanetView()
    planet_view.validate_secret_file()

    assert planet_view.w_secret_file.error_messages == []

    # Also validate with the event
    planet_view.btn.fire_event("click", None)

    # Test with non-existing file

    # Create a backup of the file
    planet_secret_file.rename(planet_secret_file.with_suffix(".json.bak"))

    planet_view.validate_secret_file()

    assert planet_view.w_secret_file.error_messages == [
        ms.planet.exception.no_secret_file
    ]

    # Restore the file
    planet_secret_file.with_suffix(".json.bak").rename(planet_secret_file)


def test_validate_event() -> None:
    """Test validation button event."""
    # Arrange
    planet_secret_file = Path.home() / ".planet.json"
    exists = False

    # if the file exists, rename it
    if planet_secret_file.exists():
        exists = True
        planet_secret_file.rename(planet_secret_file.with_suffix(".json.bak"))

    # Arrange
    planet_view = PlanetView()

    planet_view.w_method.v_model = "from_file"

    # Act
    with pytest.raises(Exception):
        planet_view.btn.fire_event("click", None)

    # Assert
    assert planet_view.alert.children[0].children == [
        ms.planet.exception.no_secret_file
    ]

    # Restore if there was a file
    if exists:
        planet_secret_file.with_suffix(".json.bak").rename(planet_secret_file)
