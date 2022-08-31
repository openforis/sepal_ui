import pytest

from sepal_ui.planetapi import PlanetModel
from sepal_ui.planetapi.planet_widgets import InfoView


class TestPlanetWidgets:
    def test_init(self):

        model = PlanetModel()
        info_view = InfoView(model=model)

        assert isinstance(info_view, InfoView)

    def test_open_info(self, no_subs, only_others, only_nicfi, all_subs):

        model = PlanetModel()
        info_view = InfoView(model=model)

        # Trigger event to check subscriptions
        model.subscriptions = {}
        model.subscriptions = no_subs

        assert info_view.get_children("nicfi").disabled
        assert info_view.get_children("others").disabled

        model.subscriptions = {}
        model.subscriptions = only_others

        assert info_view.get_children("nicfi").disabled
        assert not info_view.get_children("others").disabled

        model.subscriptions = {}
        model.subscriptions = only_nicfi

        assert not info_view.get_children("nicfi").disabled
        assert info_view.get_children("others").disabled

        model.subscriptions = {}
        model.subscriptions = all_subs

        assert not info_view.get_children("nicfi").disabled
        assert not info_view.get_children("others").disabled

        # Check the info displayed in the cards
        assert info_view.v_model == 1
        info_view.get_children("nicfi").fire_event("click", None)
        assert len(info_view.info_card.children) == len(all_subs)
        assert (
            info_view.info_card.children[0].children[0].children[0]
            == all_subs["nicfi"][0]["plan"]["name"]
        )
        assert info_view.v_model == 0

        # If we click the button two times, it will close the expansion panel
        info_view.get_children("nicfi").fire_event("click", None)
        assert info_view.v_model == 1

    @pytest.fixture
    def no_subs(self):

        return {"nicfi": [], "others": []}

    @pytest.fixture
    def only_others(self):

        return {
            "nicfi": [],
            "others": [
                {
                    "plan": {
                        "name": "level0",
                        "state": "active",
                    },
                    "active_from": "2022-03-04T02:28:03.053172+00:00",
                    "active_to": "2022-05-04T02:28:03.053172+00:00",
                },
            ],
        }

    @pytest.fixture
    def only_nicfi(self):

        return {
            "nicfi": [
                {
                    "plan": {
                        "name": "level0",
                        "state": "active",
                    },
                    "active_from": "2022-03-04T02:28:03.053172+00:00",
                    "active_to": "2022-05-04T02:28:03.053172+00:00",
                },
                {
                    "plan": {
                        "name": "level0",
                        "state": "active",
                    },
                    "active_from": "2022-03-04T02:28:03.053172+00:00",
                    "active_to": "2022-05-04T02:28:03.053172+00:00",
                },
            ],
            "others": [],
        }

    @pytest.fixture
    def all_subs(self):

        return {
            "nicfi": [
                {
                    "plan": {
                        "name": "level0",
                        "state": "active",
                    },
                    "active_from": "2022-03-04T02:28:03.053172+00:00",
                    "active_to": "2022-05-04T02:28:03.053172+00:00",
                },
                {
                    "plan": {
                        "name": "level0",
                        "state": "active",
                    },
                    "active_from": "2022-03-04T02:28:03.053172+00:00",
                    "active_to": "2022-05-04T02:28:03.053172+00:00",
                },
            ],
            "others": [
                {
                    "plan": {
                        "name": "others",
                        "state": "active",
                    },
                    "active_from": "2022-03-04T02:28:03.053172+00:00",
                    "active_to": "2022-05-04T02:28:03.053172+00:00",
                }
            ],
        }
