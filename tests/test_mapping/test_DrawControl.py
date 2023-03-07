"""Test the Draw Control."""

import math

from shapely import geometry as sg

from sepal_ui import mapping as sm


def test_init() -> None:
    """Init a drawing control."""
    m = sm.SepalMap()
    draw_control = sm.DrawControl(m)
    assert isinstance(draw_control, sm.DrawControl)

    return


def test_show() -> None:
    """Show the drawing control."""
    m = sm.SepalMap()
    draw_control = sm.DrawControl(m)

    # add it to the map
    draw_control.show()
    assert draw_control in m.controls

    # check that it's not added twice
    draw_control.show()
    assert m.controls.count(draw_control) == 1

    return


def test_hide() -> None:
    """Hide the drawing control."""
    m = sm.SepalMap()
    draw_control = sm.DrawControl(m)
    m.add(draw_control)

    # remove it
    draw_control.hide()
    assert draw_control not in m.controls

    # check that hide when not on the map doesn not raise error
    draw_control.hide()
    assert draw_control not in m.controls

    return


def test_to_json() -> None:
    """Transform the drawn feature into a geo_interface."""
    m = sm.SepalMap()
    draw_control = sm.DrawControl(m)

    # add a circle to the data
    draw_control.data = [
        {
            "type": "Feature",
            "properties": {
                "style": {
                    "stroke": True,
                    "color": "#2196F3",
                    "weight": 4,
                    "opacity": 0.5,
                    "fill": True,
                    "fillColor": None,
                    "fillOpacity": 0.2,
                    "clickable": True,
                    "radius": 50,
                }
            },
            "geometry": {"type": "Point", "coordinates": [0, 0]},
        }
    ]

    res = draw_control.to_json()
    circle = sg.shape(res["features"][0]["geometry"])

    assert res["type"] == "FeatureCollection"
    assert "features" in res
    assert "style" not in res["features"][0]["properties"]
    assert all([math.isclose(c, 0, abs_tol=0.1) for c in circle.centroid.coords[0]])
    assert len(res["features"][0]["geometry"]["coordinates"][0]) == 65

    return
