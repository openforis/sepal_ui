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
        m.add(tile_control)

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
        assert tile.get_title() == ""
        assert tile.children[0].elevation == 0

        return

    def test_update_position(self):

        # create the widget
        menu_control = sm.MenuControl("fa-solid fa-folder", sw.Card())

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

    def test_close_others(self):

        # add controls on the map
        m = sm.SepalMap()
        control_1 = sm.MenuControl("fa-solid fa-folder", sw.Card(), m=m)
        control_2 = sm.MenuControl("fa-solid fa-folder", sw.Card(), m=m)
        control_3 = sm.MenuControl("fa-solid fa-folder", sw.Card())
        m.add(control_1)
        m.add(control_2)
        m.add(control_3)

        # open the first one and then the second one
        control_1.menu.v_model = True
        control_2.menu.v_model = True
        control_3.menu.v_model = False

        # check the values
        assert control_1.menu.v_model is False
        assert control_2.menu.v_model is True
        assert control_3.menu.v_model is False

        # use the control that is not wired
        control_3.menu.v_model = True

        assert control_1.menu.v_model is False
        assert control_2.menu.v_model is True
        assert control_3.menu.v_model is True

        return
