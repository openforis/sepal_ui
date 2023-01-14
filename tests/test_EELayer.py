import ee
import pytest

from sepal_ui import mapping as sm


class TestEELayer:
    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_init(self):

        # create a point gee layer (easier to check)
        m = sm.SepalMap()
        ee_point = ee.FeatureCollection(ee.Geometry.Point(0, 0))
        m.addLayer(ee_point, {}, "point")

        assert isinstance(m.layers[1], sm.EELayer)
        assert m.layers[1].ee_object == ee_point

        return
