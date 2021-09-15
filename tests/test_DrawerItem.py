from datetime import datetime

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestDrawerItem:
    def test_init_cards(self):
        title = "toto"
        id_ = "toto_id"
        icon = "mdi-folder"

        # default init
        drawerItem = sw.DrawerItem(title)
        assert isinstance(drawerItem, v.ListItem)
        assert isinstance(drawerItem.children[0].children[0], v.Icon)
        assert drawerItem.children[0].children[0].children[0] == "mdi-folder-outline"
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
        assert drawerItem._metadata == None

        return

    def test_display_tile(self):

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
        drawer_item._on_click(None, None, None, tiles)

        # check the viz parameter of each tiles
        for tile in tiles:
            if tile.get_title() == title:
                assert tile.viz == True
            else:
                assert tile.viz == False

        return
