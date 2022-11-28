import pytest
from traitlets import Unicode

import sepal_ui.sepalwidgets as sw
from sepal_ui import color
from sepal_ui.model import Model


class TestStateIcon:
    def test_init(self, model):

        # Test with default states
        state_icon = sw.StateIcon(model, "state_value")

        assert state_icon.icon.color == color.success
        assert state_icon.children[0] == "Valid"

        # Test with custom states
        custom_states = {
            "off": ("Non connected", color.darker),
            "init": ("Initializing...", color.warning),
            "failed": ("Connection failed!", color.error),
            "successfull": ("Successfull", color.success),
        }
        state_icon = sw.StateIcon(model, "state_value", custom_states)

        assert state_icon.icon.color == color.darker
        assert state_icon.children[0] == "Non connected"

    def test_swap(self, model):

        state_icon = sw.StateIcon(model, "state_value")
        model.state_value = "non_valid"

        assert state_icon.icon.color == color.error
        assert state_icon.children[0] == "Not valid"

        # Test raise exception
        with pytest.raises(ValueError):
            model.state_value = "asdf"

    @pytest.fixture
    def model(self):
        """Dummy model with state value trait"""

        class TestModel(Model):
            state_value = Unicode().tag(sync=True)

        return TestModel()
