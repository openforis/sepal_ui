"""Test the Aoi Control."""

from typing import Tuple

import ee
import pytest
from box import Box
from shapely import geometry as sg

from sepal_ui import mapping as sm


def test_init() -> None:
    """Init an aoi_control on the map."""
    # check that the map start with no info
    m = sm.SepalMap()
    control = sm.AoiControl(m)
    m.add(control)

    assert isinstance(control, sm.AoiControl)
    assert control in m.controls

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_add_aoi_ee(
    ee_points: Tuple[ee.Geometry.Point], aoi_control: sm.AoiControl
) -> None:
    """Add a ee point to the aoi_control.

    Args:
        ee_points: a Tuple of gee points
        aoi_control: an object control
    """
    # test with an ee point
    aoi_control.add_aoi("test1", ee_points[1])
    assert aoi_control.aoi_bounds["test1"] == (20, 30, 20, 30)
    assert aoi_control.aoi_list.children[0].value == (20, 30, 20, 30)

    return


def test_add_aoi(points: Tuple[sg.Point], aoi_control: sm.AoiControl) -> None:
    """Add an aoi to the control.

    Args:
        points: a tuple of ashapely points
        aoi_control: an object control
    """
    # test ith a shapely geometry
    aoi_control.add_aoi("test1", points[0])
    assert aoi_control.aoi_bounds["test1"] == (10, 20, 10, 20)
    assert aoi_control.aoi_list.children[0].value == (10, 20, 10, 20)

    # test with something else
    with pytest.raises(ValueError):
        aoi_control.add_aoi("test3", {})

    return


def test_remove_aoi(points: Tuple[sg.Point], aoi_control: sm.AoiControl) -> None:
    """Remove an aoi from the control.

    Args:
        points: a tuple of shapely points
        aoi_control: a object control
    """
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


def test_click_btn(points: Tuple[sg.Point], aoi_control: sm.AoiControl) -> None:
    """Click on the btn to change the zoom.

    Args:
        points: a Tuple of shapely points
        aoi_control: a control object
    """
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


def test_zoom(points: Tuple[sg.Point], aoi_control: sm.AoiControl) -> None:
    """Check the map is zoomed.

    Args:
        points: a list of shapely points
        aoi_control: the control object
    """
    # add a point and zoom
    aoi_control.add_aoi("test1", points[0])
    aoi_control.zoom(Box({"value": points[0].bounds}), None, None)

    # it works but we cannot test pure JS behavior from here
    # assert aoi_control.m.center == [20.0, 10.0]
    # assert aoi_control.m.zoom == 1090.0

    return


@pytest.fixture(scope="module")
def points() -> Tuple[sg.Point]:
    """Return a tuple of points.

    Returns:
        a tuple of points
    """
    return (sg.Point(10, 20), sg.Point(20, 30))


@pytest.fixture(scope="module")
def ee_points() -> Tuple[ee.Geometry.Point]:
    """Return a tuple of ee_point.

    Returns:
        a tuple of ee points
    """
    return (ee.Geometry.Point(10, 20), ee.Geometry.Point(20, 30))


@pytest.fixture(scope="function")
def aoi_control() -> sm.AoiControl:
    """An aoi_control and add it to a map.

    Returns:
        an AoiControl object
    """
    m = sm.SepalMap()
    aoi_control = sm.AoiControl(m)
    m.add(aoi_control)

    return aoi_control
