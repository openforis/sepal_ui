import pytest

from sepal_ui import sepalwidgets as sw


class TestSepalWidget:
    def test_init(self, widget):

        assert widget.viz == True

        return

    def test_set_viz(self, widget):

        # hide the widget
        widget.viz = False
        assert "d-none" in str(widget.class_)

        # show it
        widget.viz = True
        assert not "d-none" in str(widget.class_)

        return

    def test_show(self, widget):

        widget.class_ = "d-none"
        widget.show()
        assert widget.viz == True
        assert not "d-none" in str(widget.class_)

        return

    def test_hide(self, widget):

        widget.class_ = None
        widget.hide()
        assert widget.viz == False
        assert "d-none" in str(widget.class_)

        return

    def test_toggle_viz(self, widget):

        widget.class_ = None
        assert widget.viz == True
        assert not "d-none" in str(widget.class_)

        widget.toggle_viz()
        assert widget.viz == False
        assert "d-none" in str(widget.class_)

        widget.toggle_viz()
        assert widget.viz == True
        assert not "d-none" in str(widget.class_)

        return

    def test_reset(self, widget):

        widget.v_model = "toto"

        widget.reset()

        assert widget.v_model == None

        return

    @pytest.fixture
    def widget(self):
        """return a sepalwidget"""

        return sw.SepalWidget()
