from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw


class TestMenuControl:
    def test_init(self):

        # create a tile
        tile = sw.Tile(
            "toto", "tutu", inputs=[sw.Slider()], btn=sw.Btn(), alert=sw.Alert().show()
        )

        # create the menu_control
        m = sm.SepalMap()
        tile_control = sm.MenuControl("tutu", tile)
        m.add_control(tile_control)

        # set some object in variables for easy access
        btn = tile_control.widget.v_slots[0]["children"]
        title = tile_control.widget.children[0].children[0]

        # assert all the styling
        assert tile_control in m.controls
        assert tile_control.position == "bottomright"
        assert btn.children[0] == "TUT"
        assert title.children[0] == "tutu"
        assert "ma-0" in tile.class_
        assert "pa-2" in tile.children[0].class_
        assert tile.children[0].raised is False
        assert tile.get_title() == "None"
        assert tile.children[0].elevation == 0

        return

    def test_update_position(self):

        # create the widget
        menu_control = sm.MenuControl("fas fa-folder", sw.Card())

        assert menu_control.menu.top is True
        assert menu_control.menu.bottom is False
        assert menu_control.menu.left is True
        assert menu_control.menu.right is False

        # change the position
        menu_control.position = "topleft"

        assert menu_control.menu.top is False
        assert menu_control.menu.bottom is True
        assert menu_control.menu.left is False
        assert menu_control.menu.right is True

        return
