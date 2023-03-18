"""Test the Btn widget."""

import ipyvuetify as v
import pytest

from sepal_ui import sepalwidgets as sw


def test_init() -> None:
    """Init the Btn widget."""
    # minimal btn
    btn = sw.Btn()
    assert btn.color == "primary"
    assert btn.v_icon.children[0] == ""
    assert btn.children[1] == ""

    # extensive btn
    btn = sw.Btn("toto", "fa-solid fa-folder")
    assert btn.children[1] == "toto"
    assert isinstance(btn.v_icon, v.Icon)
    assert btn.v_icon.children[0] == "fa-solid fa-folder"

    return


def test_toggle_loading(btn: sw.Btn) -> None:
    """Toggle loading status of the btn.

    Args:
        btn: a Btn object
    """
    btn = btn.toggle_loading()

    assert btn.loading is True
    assert btn.disabled is True

    btn.toggle_loading()
    assert btn.loading is False
    assert btn.disabled is False

    return


def test_set_gliph(btn: sw.Btn) -> None:
    """Dynamically set the gliph.

    Args:
        btn: a Btn object
    """
    # new gliph
    gliph = "fa-solid fa-folder"
    btn.gliph = gliph

    assert isinstance(btn.v_icon, v.Icon)
    assert btn.v_icon.children[0] == gliph
    assert btn.v_icon.left is True

    # change existing icon
    gliph = "fa-solid fa-file"
    btn.gliph = gliph
    assert btn.v_icon.children[0] == gliph

    # display only the gliph
    btn.msg = ""
    assert btn.children[1] == ""
    assert btn.v_icon.left is False

    # remove all gliph
    gliph = ""
    btn.gliph = gliph
    assert "d-none" in btn.v_icon.class_

    # assert deprecation
    with pytest.deprecated_call():
        sw.Btn(icon="fa-solid fa-folder")

    return


def test_set_msg(btn: sw.Btn) -> None:
    """Dynamically set the btn message.

    Args:
        btn: the Btn object
    """
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


@pytest.fixture(scope="function")
def btn() -> sw.Btn:
    """Create a simple btn.

    Returns:
        the btn object
    """
    return sw.Btn("Click")
