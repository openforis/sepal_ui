import ee

from sepal_ui import mapping as sm
from sepal_ui.scripts import utils as su


class TestLayerStateControl:
    def test_init(self):

        m = sm.SepalMap()
        state = sm.LayerStateControl(m)
        m.add_control(state)

        assert isinstance(state, sm.LayerStateControl)
        assert state.w_state.loading is False

        return

    @su.need_ee
    def test_change(self):

        # create the map and controls
        m = sm.SepalMap()
        state = sm.LayerStateControl(m)
        m.add_control(state)

        # add some ee_layer (loading very fast)
        # world lights
        dataset = ee.ImageCollection("NOAA/DMSP-OLS/CALIBRATED_LIGHTS_V4").filter(
            ee.Filter.date("2010-01-01", "2010-12-31")
        )
        m.addLayer(dataset, {}, "Nighttime Lights")

        # world temp
        dataset = (
            ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")
            .filter(ee.Filter.date("2020-07-01", "2020-07-02"))
            .select("temperature_2m")
        )
        m.addLayer(dataset, {}, "Air temperature [K] at 2m height")

        # TODO I don't know how to check state changes but I can at least check the conclusion
        assert state.w_state.msg == "2 layer(s) loaded"

        return
