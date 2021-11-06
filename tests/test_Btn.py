import ipyvuetify as v
import pytest

from sepal_ui import sepalwidgets as sw


class TestBtn:
    def test_init(self):

        # minimal btn
        btn = sw.Btn()
        assert btn.color == "primary"
        assert btn.v_icon.children[0] == ""
        assert btn.children[1] == "Click"

        # extensive btn
        btn = sw.Btn("toto", "mdi-folder")
        assert btn.children[1] == "toto"
        assert isinstance(btn.v_icon, v.Icon)
        assert btn.v_icon.children[0] == "mdi-folder"

        return

    def test_set_icon(self, btn):

        # new icon
        icon = "mdi-folder"
        btn = btn.set_icon(icon)

        assert isinstance(btn.v_icon, v.Icon)
        assert btn.v_icon.children[0] == icon

        # change existing icon
        icon = "mdi-file"
        btn.set_icon(icon)
        assert btn.v_icon.children[0] == icon

        return

    def test_toggle_loading(self, btn):

        btn = btn.toggle_loading()

        assert btn.loading == True
        assert btn.disabled == True

        btn.toggle_loading()
        assert btn.loading == False
        assert btn.disabled == False

        return

    @pytest.fixture
    def btn(self):
        """Create a simple btn"""

        return sw.Btn()
