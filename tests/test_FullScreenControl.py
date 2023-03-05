from sepal_ui import mapping as sm


class TestFullScreenControl:
    def test_init(self):

        # check that the map start with no info
        map_ = sm.SepalMap()

        # add a fullscreenControl
        control = sm.FullScreenControl(map_)
        map_.add(control)

        assert isinstance(control, sm.FullScreenControl)
        assert control in map_.controls
        assert control.zoomed is False
        assert "fa-solid fa-expand" in control.w_btn.children[0].children

        return

    def test_toggle_fullscreen(self):

        map_ = sm.SepalMap()
        control = sm.FullScreenControl(map_)
        map_.add(control)

        # trigger the click
        # I cannot test the javascript but i can test everything else
        control.toggle_fullscreen(None, None, None)

        assert control.zoomed is True
        assert "fa-solid fa-compress" in control.w_btn.children[0].children

        # click again to reset to initial state
        control.toggle_fullscreen(None, None, None)

        assert control.zoomed is False
        assert "fa-solid fa-expand" in control.w_btn.children[0].children

        return
