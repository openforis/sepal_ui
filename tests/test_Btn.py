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

    def test_set_gliph(self, btn):

        # new gliph
        gliph = "fas fa-folder"
        btn.gliph = gliph

        assert isinstance(btn.v_icon, v.Icon)
        assert btn.v_icon.children[0] == gliph

        # change existing icon
        gliph = "fas fa-file"
        btn.gliph = gliph
        assert btn.v_icon.children[0] == gliph

        # remove all gliph
        gliph = ""
        btn.gliph = gliph
        assert "d-none" in btn.v_icon.class_

        # assert deprecation
        with pytest.deprecated_call():
            sw.Btn(icon="fas fa-folder")

        return

    def test_test_msg(self, btn):

        # test the initial text
        assert btn.children[1] == "Click"

        # update msg
        msg = "New message"
        btn.msg = msg
        assert btn.children[1] == msg

        # test deprecation notice
        with pytest.deprecated_call():
            sw.Btn(text="Deprecation")

        return

    @pytest.fixture
    def btn(self):
        """Create a simple btn"""

        return sw.Btn()
