import unittest
import os

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestTile(unittest.TestCase):
    def test_init(self):

        # default init
        id_ = "id"
        title = "title"
        tile = sw.Tile(id_, title)

        self.assertIsInstance(tile, sw.Tile)
        self.assertEqual(tile.children[0].children[0].children[0], title)
        self.assertEqual(len(tile.children[0].children), 2)

        # exhaustive
        btn = sw.Btn()
        alert = sw.Alert()
        tile = sw.Tile(id_, title, [""], btn, alert)
        self.assertIsInstance(tile, sw.Tile)
        self.assertEqual(len(tile.children[0].children), 4)

        return

    def test_set_content(self):

        id_ = "id"
        title = "title"
        tile = sw.Tile(id_, title, alert=sw.Alert(), btn=sw.Btn())

        input_ = v.Slider()

        res = tile.set_content([input_])

        self.assertEqual(res, tile)
        self.assertEqual(tile.children[0].children[0].children[0], title)
        self.assertEqual(tile.children[0].children[1].children[0], input_)

        return

    def test_set_title(self):

        id_ = "id"
        title = "title"
        input_ = v.Slider()
        tile = sw.Tile(id_, title, [input_])

        # add a title
        title2 = "title2"
        res = tile.set_title(title2)

        self.assertEqual(res, tile)
        self.assertEqual(tile.children[0].children[0].children[0], title2)
        self.assertEqual(tile.children[0].children[1].children[0], input_)

        # remove a title
        res = tile.set_title()
        self.assertEqual(res, tile)
        self.assertEqual(tile.children[0].children[0].children[0], input_)

        return

    def test_nest(self):

        id_ = "id"
        title = "title"
        input_ = v.Slider()
        tile = sw.Tile(id_, title, [input_])

        # nest the tile
        res = tile.nest()

        self.assertEqual(res, tile)
        self.assertEqual(tile._metadata["mount_id"], "nested_tile")
        self.assertFalse(tile.elevation)
        self.assertEqual(len(tile.children[0].children), 1)

        return

    def test_hide(self):

        id_ = "id"
        title = "title"
        tile = sw.Tile(id_, title)

        res = tile.hide()

        self.assertEqual(res, tile)
        self.assertFalse(tile.viz)
        self.assertNotIn("d-inline", str(tile.class_).strip())

    def test_show(self):

        id_ = "id"
        title = "title"
        tile = sw.Tile(id_, title).hide()

        res = tile.show()

        self.assertEqual(res, tile)
        self.assertTrue(tile.viz)
        self.assertIn("d-inline", str(tile.class_).strip())

        return

    def test_toggle_inputs(self):

        inputs = []
        for i in range(5):
            inputs.append(v.Slider())

        input_2_show = v.Slider()
        inputs.append(input_2_show)

        id_ = "id"
        title = "title"
        tile = sw.Tile(id_, title, inputs)

        res = tile.toggle_inputs([input_2_show], inputs)

        self.assertEqual(res, tile)

        for input_ in inputs:
            if input_ == input_2_show:
                self.assertNotIn("d-none", str(input_.class_).strip())
            else:
                self.assertIn("d-none", str(input_.class_).strip())

        return

    def test_get_id(self):

        id_ = "id"
        tile = sw.Tile(id_, "title", [""])

        self.assertEqual(tile.get_id(), id_)

        return

    def test_tile_about(self):

        pathname = os.path.join(
            os.path.dirname(__file__), "..", "sepal_ui", "scripts", "disclaimer.md"
        )

        tile = sw.TileAbout(pathname)

        self.assertIsInstance(tile, sw.TileAbout)
        self.assertEqual(tile._metadata["mount_id"], "about_tile")

        ##########################################
        ##      didn't add a test pathname      ##
        ##########################################

        return

    def test_tile_disclaimer(self):

        tile = sw.TileDisclaimer()

        self.assertIsInstance(tile, sw.TileDisclaimer)
        self.assertEqual(tile._metadata["mount_id"], "about_tile")

        return


if __name__ == "__main__":
    unittest.main()
