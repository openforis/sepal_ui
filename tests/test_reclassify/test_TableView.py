"""Test the tableView widget."""

from sepal_ui import reclassify as rec


def test_init() -> None:
    """Check the init widget."""
    # default init
    view = rec.TableView()
    assert isinstance(view, rec.TableView)

    return


def test_get_class() -> None:
    """Nothing is tested."""
    return


def test_nest_tile() -> None:
    """Check tile is nested."""
    # nest the tile
    view = rec.TableView()
    res = view.nest_tile()

    assert res == view
    assert view._metadata["mount_id"] == "nested_tile"
    assert view.elevation == 0
    assert len(view.children[0].children) == 1

    return
