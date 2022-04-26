import os
import pytest
import planet
from sepal_ui.planetapi import PlanetModel


class TestPlanetModel:
    @pytest.fixture
    def planet_key(
        self,
    ):
        return os.environ["PLANET_API_KEY"]

    def test_init(self, planet_key):
        print(planet_key)

        # Test with a valid api key
        planet_model = PlanetModel(planet_key)

        assert isinstance(planet_model, PlanetModel)
        assert isinstance(planet_model.client, planet.api.ClientV1)
        assert planet_model.active is True

        # Test with a valid api key
        planet_model = PlanetModel("not valid")

        assert planet_model.active is False

    def test_init_client(self, planet_key):

        planet_model = PlanetModel("")

        planet_model._init_client(planet_key)
        assert planet_model.active is True

        planet_model._init_client("wrongkey")
        assert planet_model.active is False

    def test_is_active(self, planet_key):

        # Test with proper planet key
        planet_model = PlanetModel(planet_key)

        planet_model._is_active()
        assert planet_model.active is True

        planet_model = PlanetModel("wrongkey")
        planet_model._is_active()
        assert planet_model.active is False

    def test_get_subscriptions(self, planet_key):

        planet_model = PlanetModel(planet_key)

        subs = planet_model.get_subscriptions()

        # Check object has length
        assert len(subs)

    def test_get_planet_items(self, planet_key):

        # Arrange
        planet_model = PlanetModel(planet_key)

        aoi = {
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

        # Act
        items = planet_model.get_items(aoi, start, end, cloud_cover)

        # Assert
        assert items[0].get("id") == expected_first_id
