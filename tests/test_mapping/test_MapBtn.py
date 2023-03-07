from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw


def test_init() -> None:
    """Init map btn in several ways"""
    # fa-solid icon
    map_btn = sm.MapBtn("fa-solid fa-folder")
    assert isinstance(map_btn, sm.MapBtn)
    assert isinstance(map_btn.children[0], sw.Icon)
    assert map_btn.children[0].children[0] == "fa-solid fa-folder"

    # mdi icon
    map_btn = sm.MapBtn("mdi-folder")
    assert isinstance(map_btn.children[0], sw.Icon)
    assert map_btn.children[0].children[0] == "mdi-folder"

    # small text
    map_btn = sm.MapBtn("to")
    assert isinstance(map_btn.children[0], str)
    assert map_btn.children[0] == "TO"

    # long text
    map_btn = sm.MapBtn("toto")
    assert isinstance(map_btn.children[0], str)
    assert map_btn.children[0] == "TOT"

    return
