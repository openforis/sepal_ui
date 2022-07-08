import ee
import pytest
from box import Box
from shapely import geometry as sg

from sepal_ui import mapping as sm
from sepal_ui.scripts import utils as su


class TestAoiControl:
    def test_init(self):

        # check that the map start with no info
        m = sm.SepalMap()
        control = sm.AoiControl(m)
        m.add_control(control)

        assert isinstance(control, sm.AoiControl)
        assert control in m.controls

        return

    def test_add_aoi(self, point, ee_point):

        m = sm.SepalMap()
        aoi_control = sm.AoiControl(m)

        # test ith a shapely geometry
        aoi_control.add_aoi("test1", point)
        assert aoi_control.aoi_bounds["test1"] == (10, 20, 10, 20)
        assert aoi_control.aoi_list.children[0].value == (10, 20, 10, 20)

        # test with an ee point
        aoi_control.add_aoi("test1", ee_point)
        assert aoi_control.aoi_bounds["test1"] == (20, 30, 20, 30)
        assert aoi_control.aoi_list.children[0].value == (20, 30, 20, 30)

        # test with something else
        with pytest.raises(ValueError):
            aoi_control.add_aoi("test3", {})

        return

    def test_remove_aoi(self, point):

        # add a point
        m = sm.SepalMap()
        aoi_control = sm.AoiControl(m)
        aoi_control.add_aoi("test1", point)

        # test that I can remove it
        aoi_control.remove_aoi("test1")
        assert "test1" not in aoi_control.aoi_bounds
        assert len(aoi_control.aoi_list.children) == 0

        # raise error if try again
        with pytest.raises(KeyError):
            aoi_control.remove_aoi("test1")

        return

    def test_click_btn(self, point, ee_point):

        # create the map
        m = sm.SepalMap()
        m.center = [43, 25]  # anywhere
        m.zoom = 10
        aoi_control = sm.AoiControl(m)

        # zoom on it with nothing
        aoi_control.click_btn(None, None, None)

        assert m.center == [0, 0]
        assert m.zoom == 2.0

        # zoom on it with 2 points
        aoi_control.add_aoi("test1", point)
        aoi_control.add_aoi("test2", ee_point)
        aoi_control.click_btn(None, None, None)

        assert m.center == [25.0, 15.0]
        assert m.zoom == 5.0

        return

    def test_zoom(self, point):

        # add a point
        m = sm.SepalMap()
        aoi_control = sm.AoiControl(m)
        aoi_control.add_aoi("test1", point)

        # zoom on it
        aoi_control.zoom(Box({"value": point.bounds}), None, None)

        assert m.center == [20.0, 10.0]
        assert m.zoom == 1090.0

        return

    @pytest.fixture
    def point(self):
        """return a point"""

        return sg.Point(10, 20)

    @su.need_ee
    @pytest.fixture
    def ee_point(self):
        """return a ee_point"""

        return ee.Geometry.Point(20, 30)
