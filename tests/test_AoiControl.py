import ee
import pytest
from box import Box
from shapely import geometry as sg

from sepal_ui import mapping as sm


class TestAoiControl:
    def test_init(self):

        # check that the map start with no info
        m = sm.SepalMap()
        control = sm.AoiControl(m)
        m.add(control)

        assert isinstance(control, sm.AoiControl)
        assert control in m.controls

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_add_aoi_ee(self, ee_points, aoi_control):

        # test with an ee point
        aoi_control.add_aoi("test1", ee_points[1])
        assert aoi_control.aoi_bounds["test1"] == (20, 30, 20, 30)
        assert aoi_control.aoi_list.children[0].value == (20, 30, 20, 30)

        return

    def test_add_aoi(self, points, aoi_control):

        # test ith a shapely geometry
        aoi_control.add_aoi("test1", points[0])
        assert aoi_control.aoi_bounds["test1"] == (10, 20, 10, 20)
        assert aoi_control.aoi_list.children[0].value == (10, 20, 10, 20)

        # test with something else
        with pytest.raises(ValueError):
            aoi_control.add_aoi("test3", {})

        return

    def test_remove_aoi(self, points, aoi_control):

        # add a point
        aoi_control.add_aoi("test1", points[0])

        # test that I can remove it
        aoi_control.remove_aoi("test1")
        assert "test1" not in aoi_control.aoi_bounds
        assert len(aoi_control.aoi_list.children) == 0

        # raise error if try again
        with pytest.raises(KeyError):
            aoi_control.remove_aoi("test1")

        return

    def test_click_btn(self, points, aoi_control):

        # create the map
        m = aoi_control.m
        m.center = [43, 25]  # anywhere
        m.zoom = 10

        # zoom on it with nothing
        aoi_control.click_btn(None, None, None)

        assert m.center == [0, 0]
        assert m.zoom == 2.0

        # zoom on it with 2 points
        aoi_control.add_aoi("test1", points[0])
        aoi_control.add_aoi("test2", points[1])
        aoi_control.click_btn(None, None, None)

        # it works but we cannot test pure JS behavior from here
        # assert m.center == [25.0, 15.0]
        # assert m.zoom == 5.0

        return

    def test_zoom(self, points, aoi_control):

        # add a point and zoom
        aoi_control.add_aoi("test1", points[0])
        aoi_control.zoom(Box({"value": points[0].bounds}), None, None)

        # it works but we cannot test pure JS behavior from here
        # assert aoi_control.m.center == [20.0, 10.0]
        # assert aoi_control.m.zoom == 1090.0

        return

    @pytest.fixture(scope="class")
    def points(self):
        """return a tuple of points"""

        return (sg.Point(10, 20), sg.Point(20, 30))

    @pytest.fixture(scope="class")
    def ee_points(self):
        """return a tuple of ee_point"""

        return (ee.Geometry.Point(10, 20), ee.Geometry.Point(20, 30))

    @pytest.fixture
    def aoi_control(self):
        """an aoi_control and add it to a map"""

        m = sm.SepalMap()
        aoi_control = sm.AoiControl(m)
        m.add(aoi_control)

        return aoi_control
