"""Test the custom Layer Control."""

import ee
import pytest

from sepal_ui import aoi
from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_init() -> None:
    """Check the init of a layer control on a standard map."""
    # create a map with 1 layer (the basemap)
    m = sm.SepalMap()
    layer_control = next(c for c in m.controls if isinstance(c, sm.LayersControl))
    assert isinstance(layer_control.tile.children[0], sw.RadioGroup)

    layer_rows = layer_control.tile.get_children(klass=sm.LayerRow)
    base_rows = layer_control.tile.get_children(klass=sm.BaseRow)
    vector_rows = layer_control.tile.get_children(klass=sm.VectorRow)

    assert len(vector_rows) == 0
    assert len(layer_rows) == 0
    assert len(base_rows) == 1
    assert "CartoDB" in base_rows[0].children[0].children[0]

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_add_layer() -> None:
    """Check that adding a layer refresh the layer control."""
    m = sm.SepalMap()
    layer_control = next(c for c in m.controls if isinstance(c, sm.LayersControl))

    # add layers
    min, max = 2010, 2014
    for year in range(min, max):
        layer = (
            ee.ImageCollection("NOAA/DMSP-OLS/NIGHTTIME_LIGHTS")
            .filter(ee.Filter.date(f"{year}-01-01", f"{year}-12-31"))
            .select("avg_vis")
        )
        m.add_ee_layer(layer, {}, f"{year}")
    layer_rows = layer_control.tile.get_children(klass=sm.LayerRow)

    for i, year in enumerate(range(max - 1, min + 1, -1)):
        assert layer_rows[i].children[0].children[0] == f"{year}"
        assert layer_rows[i].w_slider.v_model == 1
        assert layer_rows[i].w_checkbox.v_model is True

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_add_basemaps() -> None:
    """Check that multiple basempas can be displayed at the same time."""
    m = sm.SepalMap()
    m.add_basemap("HYBRID")
    layer_control = next(c for c in m.controls if isinstance(c, sm.LayersControl))

    layer_rows = layer_control.tile.get_children(klass=sm.LayerRow)
    base_rows = layer_control.tile.get_children(klass=sm.BaseRow)

    assert len(layer_rows) == 0
    assert len(base_rows) == 2
    assert "CartoDB" in base_rows[0].children[0].children[0]
    assert "Google Satellite" in base_rows[1].children[0].children[0]

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_change_alpha() -> None:
    """Check that alpha channel can be changed."""
    m = sm.SepalMap()
    layer_control = next(c for c in m.controls if isinstance(c, sm.LayersControl))
    data = (
        ee.ImageCollection("NOAA/DMSP-OLS/NIGHTTIME_LIGHTS")
        .filter(ee.Filter.date("2010-01-01", "2010-12-31"))
        .select("avg_vis")
    )
    m.add_ee_layer(data, {}, "2010")
    layer_row = layer_control.tile.get_children(klass=sm.LayerRow)[0]
    layer = m.find_layer("2010")

    # change the alpha from the slider
    layer_row.w_slider.v_model = 0.5
    assert layer.opacity == 0.5

    # change the alpha from the layer
    layer.opacity = 0.8
    assert layer_row.w_slider.v_model == 0.8

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_select() -> None:
    """Check that layers can be selected and deselected preserving the alpha value."""
    m = sm.SepalMap()
    layer_control = next(c for c in m.controls if isinstance(c, sm.LayersControl))
    data = (
        ee.ImageCollection("NOAA/DMSP-OLS/NIGHTTIME_LIGHTS")
        .filter(ee.Filter.date("2010-01-01", "2010-12-31"))
        .select("avg_vis")
    )
    m.add_ee_layer(data, {}, "2010")
    layer_row = layer_control.tile.get_children(klass=sm.LayerRow)[0]
    layer_row.w_slider.v_model = 0.5
    layer = m.find_layer("2010")

    # make it invisible
    layer_row.w_checkbox.v_model = False
    assert layer_row.w_slider.v_model == 0.5
    assert layer.visible is False

    # set back the visibility
    layer_row.w_checkbox.v_model = True
    assert layer_row.w_slider.v_model == 0.5
    assert layer.visible is True

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_change_basemap() -> None:
    """Check that besmap can be changed and that user can select 2 at a time."""
    m = sm.SepalMap(["HYBRID", "CartoDB.Positron"])
    layer_control = next(c for c in m.controls if isinstance(c, sm.LayersControl))
    layer_rows = layer_control.tile.get_children(klass=sm.BaseRow)
    carto_row = next(
        r for r in layer_rows if r.children[0].children[0] == "CartoDB.Positron"
    )
    google_row = next(
        r for r in layer_rows if r.children[0].children[0] == "Google Satellite"
    )
    carto_layer = m.find_layer("CartoDB.Positron", base=True)
    google_layer = m.find_layer("Google Satellite", base=True)

    # select positron (their initial order is random)
    carto_row.w_radio.active = True
    assert google_row.w_radio.active is False
    assert google_layer.visible is False
    assert carto_layer.visible is True

    # select google
    google_row.w_radio.active = True
    assert carto_row.w_radio.active is False
    assert google_layer.visible is True
    assert carto_layer.visible is False

    # do it from the layers
    carto_layer.visible = True
    assert google_row.w_radio.active is False
    assert carto_row.w_radio.active is True
    assert google_layer.visible is False

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_ungrouped() -> None:
    """Check that layer control can be displayed at the same time with other menus."""
    m = sm.SepalMap(["HYBRID", "CartoDB.Positron"], vinspector=True)
    layer_control = next(c for c in m.controls if isinstance(c, sm.LayersControl))
    m.v_inspector.menu.v_model = True

    # open the layer_control
    layer_control.menu.v_model = True
    assert m.v_inspector.menu.v_model is True

    return


def test_vectors() -> None:
    """Check that vectors are grouped together and they can be controlled."""
    m = sm.SepalMap()
    m.add_layer(aoi.AoiModel(admin="171").get_ipygeojson())
    aoi_layer = m.find_layer("aoi")
    layer_control = next(c for c in m.controls if isinstance(c, sm.LayersControl))
    vector_rows = layer_control.tile.get_children(klass=sm.VectorRow)
    vector_row = vector_rows[0]

    assert len(vector_rows) == 1

    # set visibility from the btn
    vector_row.w_checkbox.v_model = False
    assert aoi_layer.visible is False

    # set the visibility from the layer
    aoi_layer.visible = True
    assert vector_row.w_checkbox.v_model is True

    return
