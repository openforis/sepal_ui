import unittest

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestApp(unittest.TestCase):
    def test_init(self):

        # default init
        app = sw.App()
        self.assertIsInstance(app, sw.App)
        self.assertEqual(len(app.children), 3)
        self.assertIsInstance(app.children[0], v.Overlay)
        self.assertIsInstance(app.children[1], sw.AppBar)
        self.assertIsInstance(app.children[2], v.Content)

        # exhaustive
        navDrawer = sw.NavDrawer([sw.DrawerItem(f"title {i}") for i in range(5)])
        appBar = sw.AppBar()
        tiles = []
        for i in range(5):
            tiles.append(sw.Tile(f"id_{i}", f"title_{i}"))
        footer = sw.Footer()

        app = sw.App(tiles, appBar, footer, navDrawer)
        self.assertIsInstance(app, sw.App)
        self.assertEqual(len(app.children), 5)
        self.assertIsInstance(app.children[0], v.Overlay)
        self.assertIsInstance(app.children[1], sw.AppBar)
        self.assertIsInstance(app.children[2], sw.NavDrawer)
        self.assertIsInstance(app.children[3], v.Content)
        self.assertIsInstance(app.children[4], sw.Footer)

        return

    def test_show_tile(self):

        tiles = [sw.Tile(f"id_{i}", f"title_{i}") for i in range(5)]
        drawer_items = [sw.DrawerItem(f"title {i}", card=f"id_{i}") for i in range(5)]
        appBar = sw.AppBar()
        footer = sw.Footer()

        title = "main_title"
        id_ = "main_id"
        main_tile = sw.Tile(id_, title)
        main_drawer = sw.DrawerItem(title, card=id_)
        tiles.append(main_tile)
        drawer_items.append(main_drawer)

        app = sw.App(tiles, appBar, footer, sw.NavDrawer(drawer_items))
        res = app.show_tile(id_)

        self.assertEqual(res, app)

        for tile in tiles:
            if tile == main_tile:
                self.assertTrue(tile.viz)
            else:
                self.assertFalse(tile.viz)

        for di in drawer_items:
            if di._metadata["card_id"] == id_:
                self.assertTrue(di.input_value)
            else:
                self.assertFalse(di.input_value)


if __name__ == "__main__":
    unittest.main()
