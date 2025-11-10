"""Test the DrawerItem widget."""

import ipyvuetify as v
import pytest
from traitlets import Bool

from sepal_ui import sepalwidgets as sw
from sepal_ui.model import Model


class LocalModel(Model):
    """A test model with one single trait."""

    app_ready = Bool(False).tag(sync=True)


def test_init_cards() -> None:
    """Check init the widgets."""
    title = "toto"
    id_ = "toto_id"
    icon = "fa-solid fa-folder"

    # default init
    drawerItem = sw.DrawerItem(title)
    assert isinstance(drawerItem, v.VuetifyTemplate)
    assert isinstance(drawerItem.children[0].children[0], v.Icon)
    assert drawerItem.children[0].children[0].children[0] == "fa-regular fa-folder"
    assert isinstance(drawerItem.children[1].children[0], v.ListItemTitle)
    assert drawerItem.children[1].children[0].children[0] == title

    # exhaustive
    drawerItem = sw.DrawerItem(title, icon, id_)
    assert drawerItem.children[0].children[0].children[0] == icon
    assert drawerItem.children[1].children[0].children[0] == title
    assert drawerItem._metadata["card_id"] == id_

    # too much args
    drawerItem = sw.DrawerItem(title, icon, id_, "#")
    assert drawerItem.href == "#"
    assert drawerItem.target == "_blank"
    assert drawerItem._metadata is None

    return


def test_display_tile() -> None:
    """Display the tile that is associated with the widget."""
    # build fake tiles
    tiles = []
    for i in range(5):
        title = f"name_{i}"
        id_ = f"id_{i}"
        tiles.append(sw.Tile(id_, title))

    # create the real tile
    title = "toto"
    id_ = "toto_id"
    real_tile = sw.Tile(id_, title)
    tiles.append(real_tile)

    # create the drawer item and bind it to the tiles
    drawer_item = sw.DrawerItem(title, card=id_).display_tile(tiles)

    # fake the click
    drawer_item._on_click(tiles)

    # check the viz parameter of each tiles
    for tile in tiles:
        if tile.get_title() == title:
            assert tile.viz is True
        else:
            assert tile.viz is False

    return


def test_add_notif(model: LocalModel, drawer_item: sw.DrawerItem) -> None:
    """Check notification is added to the drawer.

    Args:
        model: the model piloting the status of the tile
        drawer_item: a drawer item associated to the model
    """
    model.app_ready = True
    assert drawer_item.alert_badge in drawer_item.children

    model.app_ready = False
    assert drawer_item.alert_badge not in drawer_item.children

    return


def test_remove_notif(model: LocalModel, drawer_item: sw.DrawerItem) -> None:
    """Check notification can be removed.

    Args:
        model: the model piloting the status of the tile
        drawer_item: a drawer item associated to the model
    """
    model.app_ready = True
    drawer_item.remove_notif()
    assert drawer_item.alert_badge not in drawer_item.children

    return


@pytest.fixture(scope="function")
def model() -> LocalModel:
    """A test model instance.

    Returns:
        the object instance
    """
    return LocalModel()


@pytest.fixture(scope="function")
def drawer_item(model: LocalModel) -> sw.DrawerItem:
    """Create dummy drawer item.

    Args:
        model: the test_model to update drawer status
    """
    return sw.DrawerItem("title", model=model, bind_var="app_ready")
