from sepal_ui import mapping as sm


class TestDrawControl:
    def test_init(self):

        m = sm.SepalMap()
        draw_control = sm.DrawControl(m)
        assert isinstance(draw_control, sm.DrawControl)

        return

    def test_show(self):

        m = sm.SepalMap()
        draw_control = sm.DrawControl(m)

        # add it to the map
        draw_control.show()
        assert draw_control in m.controls

        # check that it's not added twice
        draw_control.show()
        assert m.controls.count(draw_control) == 1

        return

    def test_hide(self):

        m = sm.SepalMap()
        draw_control = sm.DrawControl(m)
        m.add_control(draw_control)

        # remove it
        draw_control.hide()
        assert draw_control not in m.controls

        # check that hide when not on the map doesn not raise error
        draw_control.hide()
        assert draw_control not in m.controls

        return
