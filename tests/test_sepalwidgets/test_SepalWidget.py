"""Test the SepalWidget meta class"""

import pytest

from sepal_ui import sepalwidgets as sw


def test_init() -> None:
    """Test widget init"""

    widget = sw.SepalWidget()

    assert widget.viz is True

    return


def test_set_viz() -> None:
    """Check viz can be changed"""

    widget = sw.SepalWidget()

    # hide the widget
    widget.viz = False
    assert "d-none" in str(widget.class_)

    # show it
    widget.viz = True
    assert "d-none" not in str(widget.class_)

    return


def test_show() -> None:
    """Check show method can force show a widget"""

    widget = sw.SepalWidget()

    widget.viz = False
    widget.show()
    assert widget.viz is True
    assert "d-none" not in str(widget.class_)

    return


def test_hide() -> None:
    """Check hide can force hide a widget"""

    widget = sw.SepalWidget()

    widget.class_ = None
    widget.hide()
    assert widget.viz is False
    assert "d-none" in str(widget.class_)

    return


def test_toggle_viz() -> None:
    """Check visibility can be toggled"""

    widget = sw.SepalWidget()

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


def test_reset() -> None:
    """Check widget implement a reset method"""

    widget = sw.SepalWidget()

    widget.v_model = "toto"

    widget.reset()

    assert widget.v_model is None

    return


def test_set_children() -> None:
    """Check children can be added in specific index"""
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

    return


def test_set_children_error() -> None:
    """Test when set_children methods throws an error."""
    with pytest.raises(ValueError):
        sw.Card().set_children("asdf", "middle")

    return


def test_get_children() -> None:
    """Check get_children can identify and list the target children widgets"""

    test_card = sw.Card()

    # fill with card with multiple attributes and widgets
    alerts = [sw.Alert(attributes={"id": i}) for i in range(5)]
    cards = [sw.Card(attributes={"id": i}, children=alerts) for i in range(5)]
    btns = [sw.Btn(attributes={"id": i}) for i in range(5)]
    test_card.children = cards + btns

    # search for specific class
    res = test_card.get_children(klass=sw.Card)
    assert len(res) == 5
    assert all(isinstance(w, sw.Card) for w in res)

    # no match search class
    res = test_card.get_children(klass=sw.Badge)
    assert len(res) == 0

    # search for specific attributes in any class
    res = test_card.get_children(attr="id", value=3)
    assert len(res) == 7
    assert isinstance(res[0], sw.Alert)
    assert isinstance(res[1], sw.Alert)
    assert isinstance(res[2], sw.Alert)
    assert isinstance(res[3], sw.Card)
    assert isinstance(res[4], sw.Alert)
    assert isinstance(res[5], sw.Alert)
    assert isinstance(res[6], sw.Btn)

    # missing value (all children will match including icons)
    res = test_card.get_children(attr="id")
    assert len(res) == 40

    # missing attr (all children will match including icons)
    res = test_card.get_children(value=5)
    assert len(res) == 40

    # no match search attr
    res = test_card.get_children(attr="toto", value="toto")
    assert len(res) == 0

    # mixed search
    res = test_card.get_children(klass=sw.Alert, attr="id", value=4)
    assert len(res) == 5
    assert isinstance(res[0], sw.Alert)
    assert res[0].attributes.get("id") == 4

    # check for old implementation
    res = test_card.get_children(id_=3)
    eq = test_card.get_children(attr="id", value=3)
    assert len(res) == len(eq)
    assert all(r == e for r, e in zip(res, eq))

    return
