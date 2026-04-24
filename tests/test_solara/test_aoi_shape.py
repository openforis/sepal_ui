"""Tests for process_shape."""

import asyncio
from pathlib import Path

import pytest

from pysepal.solara.components.aoi.shape import process_shape

DATA = Path(__file__).resolve().parents[1] / "data" / "aoi_manual"
GEOJSON = DATA / "manual_polygons.geojson"
KML = DATA / "manual_zones.kml"


def _run(coro):
    return asyncio.run(coro)


def test_process_shape_rejects_empty_path():
    with pytest.raises(ValueError):
        _run(process_shape("", gee=False))


def test_process_shape_rejects_column_without_value():
    with pytest.raises(ValueError):
        _run(process_shape(str(GEOJSON), column="region", value=None, gee=False))


def test_process_shape_loads_geojson():
    result = _run(process_shape(str(GEOJSON), gee=False))

    assert result.method == "SHAPE"
    assert result.gee is False
    assert result.feature_collection is None
    assert result.gdf.crs.to_epsg() == 4326
    assert not result.gdf.empty


def test_process_shape_filters_by_column_value():
    all_result = _run(process_shape(str(GEOJSON), gee=False))
    region_values = all_result.gdf["region"].unique().tolist()
    target = region_values[0]

    result = _run(process_shape(str(GEOJSON), column="region", value=target, gee=False))

    assert (result.gdf["region"] == target).all()
    assert result.name.endswith(f"_{target}")


def test_process_shape_raises_when_filter_has_no_match():
    with pytest.raises(ValueError, match="No features found"):
        _run(process_shape(str(GEOJSON), column="region", value="does-not-exist", gee=False))


def test_process_shape_strips_z_coordinates_from_kml():
    result = _run(process_shape(str(KML), gee=False))

    # KML inputs typically carry Z; process_shape must flatten them for EE compat.
    assert not result.gdf.geometry.has_z.any()
