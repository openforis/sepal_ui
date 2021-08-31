import unittest
from datetime import datetime

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestDrawerItem(unittest.TestCase):
    def test_init_cards(self):
        title = "toto"
        id_ = "toto_id"
        icon = "mdi-folder"

        # default init
        drawerItem = sw.DrawerItem(title)
        self.assertIsInstance(drawerItem, v.ListItem)
        self.assertIsInstance(drawerItem.children[0].children[0], v.Icon)
        self.assertEqual(
            drawerItem.children[0].children[0].children[0], "mdi-folder-outline"
        )
        self.assertIsInstance(drawerItem.children[1].children[0], v.ListItemTitle)
        self.assertEqual(drawerItem.children[1].children[0].children[0], title)

        # exhaustive
        drawerItem = sw.DrawerItem(title, icon, id_)
        self.assertEqual(drawerItem.children[0].children[0].children[0], icon)
        self.assertEqual(drawerItem.children[1].children[0].children[0], title)
        self.assertEqual(drawerItem._metadata["card_id"], id_)

        # too much args
        drawerItem = sw.DrawerItem(title, icon, id_, "#")
        self.assertEqual(drawerItem.href, "#")
        self.assertEqual(drawerItem.target, "_blank")
        self.assertEqual(drawerItem._metadata, None)

        return

    def test_display_tile(self):

        # build fake tiles
        tiles = []
        for i in range(5):
            title = "name_{}".format(i)
            id_ = "id_{}".format(i)
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
                self.assertTrue(tile.viz)
            else:
                self.assertFalse(tile.viz)

        return


if __name__ == "__main__":
    unittest.main()
