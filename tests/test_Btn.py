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
        btn = sw.Btn("toto", "fas fa-folder")
        assert btn.children[1] == "toto"
        assert isinstance(btn.v_icon, v.Icon)
        assert btn.v_icon.children[0] == "fas fa-folder"

        return

    def test_set_icon(self, btn):

        # new icon
        icon = "fas fa-folder"
        btn = btn.set_icon(icon)

        assert isinstance(btn.v_icon, v.Icon)
        assert btn.v_icon.children[0] == icon

        # change existing icon
        icon = "fas fa-file"
        btn.set_icon(icon)
        assert btn.v_icon.children[0] == icon

        return

    def test_toggle_loading(self, btn):

        btn = btn.toggle_loading()

        assert btn.loading is True
        assert btn.disabled is True

        btn.toggle_loading()
        assert btn.loading is False
        assert btn.disabled is False

        return

    @pytest.fixture
    def btn(self):
        """Create a simple btn"""

        return sw.Btn()
