from pathlib import Path

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestTile:
    def test_init(self):

        # default init
        id_ = "id"
        title = "title"
        tile = sw.Tile(id_, title)

        assert isinstance(tile, sw.Tile)
        assert tile.children[0].children[0].children[0] == title
        assert len(tile.children[0].children) == 2

        # exhaustive
        btn = sw.Btn()
        alert = sw.Alert()
        tile = sw.Tile(id_, title, [""], btn, alert)
        assert isinstance(tile, sw.Tile)
        assert len(tile.children[0].children) == 4

        return

    def test_set_content(self):

        id_ = "id"
        title = "title"
        tile = sw.Tile(id_, title, alert=sw.Alert(), btn=sw.Btn())

        input_ = v.Slider()

        res = tile.set_content([input_])

        assert res == tile
        assert tile.children[0].children[0].children[0] == title
        assert tile.children[0].children[1].children[0] == input_

        return

    def test_set_title(self):

        id_ = "id"
        title = "title"
        input_ = v.Slider()
        tile = sw.Tile(id_, title, [input_])

        # add a title
        title2 = "title2"
        res = tile.set_title(title2)

        assert res == tile
        assert tile.children[0].children[0].children[0] == title2
        assert tile.children[0].children[1].children[0] == input_

        # remove a title
        res = tile.set_title()
        assert res == tile
        assert tile.children[0].children[0].children[0] == input_

        return

    def test_nest(self):

        id_ = "id"
        title = "title"
        input_ = v.Slider()
        tile = sw.Tile(id_, title, [input_])

        # nest the tile
        res = tile.nest()

        assert res == tile
        assert tile._metadata["mount_id"] == "nested_tile"
        assert tile.elevation == False
        assert len(tile.children[0].children) == 1

        return

    def test_hide(self):

        id_ = "id"
        title = "title"
        tile = sw.Tile(id_, title)

        res = tile.hide()

        assert res == tile
        assert tile.viz == False
        assert not "d-inline" in tile.class_

        return

    def test_show(self):

        id_ = "id"
        title = "title"
        tile = sw.Tile(id_, title).hide()

        res = tile.show()

        assert res == tile
        assert tile.viz == True
        assert "d-inline" in tile.class_

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

        assert res == tile

        for input_ in inputs:
            if input_ == input_2_show:
                assert not "d-none" in str(input_.class_)
            else:
                assert "d-none" in input_.class_

        return

    def test_get_id(self):

        id_ = "id"
        tile = sw.Tile(id_, "title", [""])

        assert tile.get_id() == id_

        return

    def test_tile_about(self):

        pathname = (
            Path(__file__).parent / ".." / "sepal_ui" / "scripts" / "disclaimer.md"
        )

        tile = sw.TileAbout(pathname)

        assert isinstance(tile, sw.TileAbout)
        assert tile._metadata["mount_id"] == "about_tile"

        ##########################################
        ##      didn't add a test pathname      ##
        ##########################################

        return

    def test_tile_disclaimer(self):

        tile = sw.TileDisclaimer()

        assert isinstance(tile, sw.TileDisclaimer)
        assert tile._metadata["mount_id"] == "about_tile"

        return
