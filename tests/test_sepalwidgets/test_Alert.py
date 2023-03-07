"""Test the Alert widget"""

import pytest

from sepal_ui import sepalwidgets as sw
from sepal_ui.frontend.styles import TYPES
from sepal_ui.scripts.warning import SepalWarning


def test_init() -> None:
    """Test widget init"""
    # default init
    alert = sw.Alert()
    assert alert.viz is False
    assert alert.type == "info"

    # every legit types
    for type_ in TYPES:
        alert = sw.Alert(type_)
        assert alert.type == type_

    # wrong type
    with pytest.warns(SepalWarning):
        alert = sw.Alert("random")
        assert alert.type == "info"

    return


def test_add_msg() -> None:
    """Check alert can receive new messagess"""
    alert = sw.Alert()
    msg = "toto"

    # single msg
    res = alert.add_msg(msg)
    assert res == alert
    assert alert.viz is True
    assert alert.children[0].children[0] == msg

    # single msg with type
    for type_ in TYPES:
        alert.add_msg(msg, type_)
        assert alert.type == type_
        assert alert.children[0].children[0] == msg

    # single msg with rdm type
    with pytest.warns(SepalWarning):
        alert.add_msg(msg, "random")
        assert alert.type == "info"
        assert alert.children[0].children[0] == msg

    return


def test_add_live_msg() -> None:
    """Check alert can receive new live messages"""

    alert = sw.Alert()
    msg = "toto"

    # single msg
    res = alert.add_live_msg(msg)
    assert res == alert
    assert alert.viz is True
    assert alert.children[1].children[0] == msg

    # single msg with type
    for type_ in TYPES:
        alert.add_live_msg(msg, type_)
        assert alert.type == type_
        assert alert.children[1].children[0] == msg

    # single msg with rdm type
    with pytest.warns(SepalWarning):
        alert.add_live_msg(msg, "random")
        assert alert.type == "info"
        assert alert.children[1].children[0] == msg

    return


def test_append_msg() -> None:
    """Check I can append new messages to alert object"""

    alert = sw.Alert()
    start = "toto"
    msg = "tutu"

    # test from empty alert
    alert = sw.Alert()
    res = alert.append_msg(msg)

    assert res == alert
    assert len(alert.children) == 1
    assert alert.children[0].children[0] == msg

    # test from non empty alert without divider
    alert = sw.Alert().add_msg(start)
    res = alert.append_msg(msg)

    assert res == alert
    assert len(alert.children) == 2
    assert alert.children[0].children[0] == start
    assert alert.children[1].children[0] == msg

    # test from non empty alert with divider
    alert = sw.Alert().add_msg(start)
    res = alert.append_msg(msg, section=True)

    assert res == alert
    assert len(alert.children) == 3
    assert alert.children[0].children[0] == start
    assert isinstance(alert.children[1], sw.Divider)
    assert alert.children[2].children[0] == msg

    # check that the divider is changing color
    alert.type = "success"
    assert alert.children[1].type_ == "success"


def test_reset() -> None:
    """Check alert object can be reset"""

    alert = sw.Alert()
    alert.add_msg("toto").reset()

    assert alert.viz is False
    assert len(alert.children) == 1
    assert alert.children[0] == ""

    return


def test_rmv_last_msg() -> None:
    """Check last message can be removed"""

    # check with a no msg alert
    alert = sw.Alert().remove_last_msg()

    assert alert.viz is False
    assert alert.children[0] == ""

    # check with a 1 msg alert
    alert = sw.Alert().add_msg("toto").remove_last_msg()

    assert alert.viz is False
    assert alert.children[0] == ""

    # check with a multiple msg alert
    alert = sw.Alert()

    string = "toto"
    nb_msg = 5
    for i in range(nb_msg):
        alert.append_msg(f"{string}{i}")

    alert.remove_last_msg()

    assert alert.viz is True
    assert len(alert.children) == 4
    assert alert.children[nb_msg - 2].children[0] == f"{string}{nb_msg-2}"

    return


def test_update_progress() -> None:
    """Check alert can embed tqdm output"""

    # test a random update
    alert = sw.Alert()
    alert.update_progress(0.5)
    assert alert.progress_bar.n == 0.5
    assert alert.viz is True

    # show that a value > 1 raise an error
    with pytest.raises(ValueError):
        alert.reset()
        alert.update_progress(1.5)

    # check that if total is set value can be more than 1
    alert.reset()
    alert.update_progress(50, total=100)
    assert alert.progress_bar.n == 50
    assert alert.viz is True

    return
