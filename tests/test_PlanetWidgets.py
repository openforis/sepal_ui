import pytest

from sepal_ui.planetapi import PlanetModel
from sepal_ui.planetapi.planet_widgets import InfoView


class TestPlanetWidgets:
    def test_init(self, info_view):

        model = PlanetModel()
        info_view = InfoView(model=model)

        assert isinstance(info_view, InfoView)

        return

    def test_open_info(self, no_subs, only_others, only_nicfi, all_subs, info_view):

        nicfi_sub = info_view.get_children(attr="id", value="nicfi")[0]
        other_sub = info_view.get_children(attr="id", value="others")[0]

        # Trigger event to check subscriptions
        info_view.model.subscriptions = {}
        info_view.model.subscriptions = no_subs
        assert nicfi_sub.disabled is True
        assert other_sub.disabled is True

        info_view.model.subscriptions = {}
        info_view.model.subscriptions = only_others
        assert nicfi_sub.disabled is True
        assert other_sub.disabled is False

        info_view.model.subscriptions = {}
        info_view.model.subscriptions = only_nicfi
        assert nicfi_sub.disabled is False
        assert other_sub.disabled is True

        info_view.model.subscriptions = {}
        info_view.model.subscriptions = all_subs
        assert nicfi_sub.disabled is False
        assert other_sub.disabled is False

        # Check the info displayed in the cards
        assert info_view.v_model == 1
        nicfi_sub.fire_event("click", None)
        assert len(info_view.info_card.children) == len(all_subs)
        assert (
            info_view.info_card.children[0].children[0].children[0]
            == all_subs["nicfi"][0]["plan"]["name"]
        )
        assert info_view.v_model == 0

        # If we click the button two times, it will close the expansion panel
        nicfi_sub.fire_event("click", None)
        assert info_view.v_model == 1

        return

    @pytest.fixture(scope="class")
    def no_subs(self):

        return {"nicfi": [], "others": []}

    @pytest.fixture(scope="class")
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

    @pytest.fixture(scope="class")
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

    @pytest.fixture(scope="class")
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

    @pytest.fixture
    def info_view(self):
        """InfoView widget."""
        return InfoView(model=PlanetModel())
