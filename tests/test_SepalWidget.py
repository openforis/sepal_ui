import pytest

from sepal_ui import sepalwidgets as sw


class TestSepalWidget:
    def test_init(self, widget):

        assert widget.viz is True

        return

    def test_set_viz(self, widget):

        # hide the widget
        widget.viz = False
        assert "d-none" in str(widget.class_)

        # show it
        widget.viz = True
        assert "d-none" not in str(widget.class_)

        return

    def test_show(self, widget):

        widget.viz = False
        widget.show()
        assert widget.viz is True
        assert "d-none" not in str(widget.class_)

        return

    def test_hide(self, widget):

        widget.class_ = None
        widget.hide()
        assert widget.viz is False
        assert "d-none" in str(widget.class_)

        return

    def test_toggle_viz(self, widget):

        widget.class_ = None
        assert widget.viz is True
        assert "d-none" not in str(widget.class_)

        widget.toggle_viz()
        assert widget.viz is False
        assert "d-none" in str(widget.class_)

        widget.toggle_viz()
        assert widget.viz is True
        assert "d-none" not in str(widget.class_)

        return

    def test_reset(self, widget):

        widget.v_model = "toto"

        widget.reset()

        assert widget.v_model is None

        return

    def test_set_children(self):

        test_card = sw.Card()

        # Test that new element is at the end of the children
        test_card.set_children("asdf", "last")
        assert test_card.children[-1] == "asdf"

        # Test that new element is at the begining (default)
        test_card.set_children("asdf")
        assert test_card.children[0] == "asdf"

        # Test we can add more than one element as a list
        new_els = [sw.Icon(), "asdf"]
        test_card.set_children(new_els)
        assert test_card.children[: len(new_els)] == new_els

    def test_set_children_error(self):
        """Test when set_children methods throws an error"""

        with pytest.raises(ValueError):
            sw.Card().set_children("asdf", "middle")

    def test_get_children(self):

        # Arrange with multiple childrens with same id
        test_card = sw.Card()
        match_card = sw.Card(attributes={"id": "asdf"})

        test_card.set_children([match_card] * 2, position="first")

        expected_output = [match_card] * 2

        assert isinstance(test_card.get_children(id_="asdf"), list)
        assert test_card.get_children(id_="asdf") == expected_output

        # Arrange without any match
        test_card = sw.Card()

        # The result will be an empty list
        assert not test_card.get_children(id_="asdf")

        # Arrange with a nested element
        test_card = sw.Card()
        test_card.set_children(sw.Card(children=[match_card]))

        assert test_card.get_children(id_="asdf") == match_card

        # Be sure we are only getting the element (not list) when there's only one match
        assert type(test_card.get_children(id_="asdf")) == type(match_card)

    @pytest.fixture
    def widget(self):
        """return a sepalwidget"""

        return sw.SepalWidget()
