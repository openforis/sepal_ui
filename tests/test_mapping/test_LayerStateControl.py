"""Test the LayerState control."""

import ee
import pytest
from ipyleaflet import RasterLayer
from traitlets import Bool

from sepal_ui import mapping as sm


def test_init() -> None:
    """Init a control object."""
    m = sm.SepalMap()
    state = sm.LayerStateControl(m)
    m.add(state)

    assert isinstance(state, sm.LayerStateControl)
    assert state.w_state.loading is False

    return


@pytest.mark.skipif(not ee.data.is_initialized(), reason="GEE is not set")
def test_update_nb_layer(map_with_layers: sm.SepalMap) -> None:
    """Check that number of layer is dynamically updated.

    Args:
        map_with_layers: a map supporting 2 FakeLayer
    """
    # create the map and controls
    m = map_with_layers
    state = next(c for c in m.controls if isinstance(c, sm.LayerStateControl))

    # TODO I don't know how to check state changes but I can at least check the conclusion
    assert state.w_state.msg == "2 layer(s) loaded"

    # remove a layer to update the nb_layer
    m.remove_layer(-1)
    assert state.w_state.msg == "1 layer(s) loaded"

    return


@pytest.mark.skipif(not ee.data.is_initialized(), reason="GEE is not set")
def test_update_loading(map_with_layers: sm.SepalMap) -> None:
    """Check loading control is updated when a layer is loading.

    Args:
        map_with_layers: a map supporting 2 FakeLayer
    """
    # get the map and control
    m = map_with_layers
    state = next(c for c in m.controls if isinstance(c, sm.LayerStateControl))

    # check that the parameter is updated with existing layers
    m.layers[-1].loading = True
    assert state.nb_loading_layer == 1
    assert state.w_state.msg == "loading 1 layer(s) out of 2"

    # check when this loading layer is removed
    m.remove_layer(-1)
    assert state.nb_loading_layer == 0
    assert state.w_state.msg == "1 layer(s) loaded"

    return


@pytest.fixture(scope="function")
def map_with_layers() -> sm.SepalMap:
    """Create a map with 2 layers and a stateBar."""
    # create the map and controls
    m = sm.SepalMap()
    state = sm.LayerStateControl(m)
    m.add(state)

    # add some ee_layer (loading very fast)
    # world lights
    dataset = ee.ImageCollection("NOAA/DMSP-OLS/CALIBRATED_LIGHTS_V4").filter(
        ee.Filter.date("2010-01-01", "2010-12-31")
    )
    m.addLayer(dataset, {}, "Nighttime Lights")

    # a fake layer with loading update possibilities
    m.add_layer(FakeLayer())

    return m


class FakeLayer(RasterLayer):
    """Layer class that have only one parameter: the loading trait."""

    loading = Bool(False).tag(sync=True)
