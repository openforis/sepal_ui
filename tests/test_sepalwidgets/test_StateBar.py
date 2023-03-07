"""Test the StateBar widget."""

from sepal_ui import sepalwidgets as sw


def test_init() -> None:
    """Check init the widget."""
    # minimal state bar
    state_bar = sw.StateBar()
    assert len(state_bar.children) == 2
    assert state_bar.viz is True

    return


def test_add_msg() -> None:
    """Check that a message can be added."""
    state_bar = sw.StateBar()

    # assert that add msg can add a msg without blocking the loading
    msg = "not finished"
    state_bar.add_msg(msg, True)

    assert state_bar.children[0].indeterminate is True
    assert state_bar.msg == msg

    # assert that add message can stop the loading
    msg = "finished"
    state_bar.add_msg(msg)

    assert state_bar.children[0].indeterminate is False

    return
