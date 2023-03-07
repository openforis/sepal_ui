import ee
import pytest

from sepal_ui import mapping as sm


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_init() -> None:
    """Init a EELyer and check members"""
    # create a point gee layer (easier to check)
    m = sm.SepalMap()
    ee_point = ee.FeatureCollection(ee.Geometry.Point(0, 0))
    m.addLayer(ee_point, {}, "point")

    layer = m.find_layer("point")
    assert isinstance(layer, sm.EELayer)
    assert layer.ee_object == ee_point

    return
