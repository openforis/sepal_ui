import pytest
import sepal_ui.sepalwidgets as sw
from sepal_ui import color
from sepal_ui.model import Model
from traitlets import Unicode


class TestStateIcon:
    @pytest.fixture
    def model(self):
        """Dummy model with state value trait"""

        class TestModel(Model):
            state_value = Unicode().tag(sync=True)

        return TestModel()

    def test_init(self, model):

        # Test with default states
        state_icon = sw.StateIcon(model, "state_value")

        assert state_icon.icon.color == color.success
        assert state_icon.children[0] == "Valid"

        # Test with custom states

        # Arrange
        custom_states = {
            "off": ("Non connected", color.darker),
            "init": ("Initializing...", color.warning),
            "failed": ("Connection failed!", color.error),
            "successfull": ("Successfull", color.success),
        }

        # Act
        state_icon = sw.StateIcon(model, "state_value", custom_states)

        # Assert
        assert state_icon.icon.color == color.darker
        assert state_icon.children[0] == "Non connected"

    def test_swap(self, model):

        # Arrange
        state_icon = sw.StateIcon(model, "state_value")

        # Act
        model.state_value = "non_valid"

        # Assert
        assert state_icon.icon.color == color.error
        assert state_icon.children[0] == "Not valid"

        # Test raise exception

        with pytest.raises(ValueError):
            model.state_value = "asdf"
