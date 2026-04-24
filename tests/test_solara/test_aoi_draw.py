"""Tests for process_draw."""

import pytest

from pysepal.solara.components.aoi.draw import process_draw


def _single_polygon_feature(properties: dict) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": properties,
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                },
            }
        ],
    }


def test_process_draw_rejects_empty_geojson():
    with pytest.raises(ValueError):
        process_draw({}, gee=False)


def test_process_draw_rejects_missing_features():
    with pytest.raises(ValueError):
        process_draw({"type": "FeatureCollection", "features": []}, gee=False)


def test_process_draw_strips_style_property():
    geo = _single_polygon_feature({"name": "keep", "style": {"color": "red"}})

    result = process_draw(geo, name="plot", gee=False)

    assert "style" not in result.gdf.iloc[0]
    assert result.gdf.iloc[0]["name"] == "keep"


def test_process_draw_normalizes_user_name():
    geo = _single_polygon_feature({})

    result = process_draw(geo, name="My Plot / 2026", gee=False)

    # normalize_str replaces spaces and slashes with underscores
    assert result.name == "My_Plot___2026"


def test_process_draw_generates_timestamped_name_when_empty():
    geo = _single_polygon_feature({})

    result = process_draw(geo, name="", gee=False)

    assert result.name.startswith("drawn_")
    # YYYYMMDD_HHMMSS -> 8 + 1 + 6 characters
    assert len(result.name) == len("drawn_") + 15


def test_process_draw_returns_aoi_result_with_gdf():
    geo = _single_polygon_feature({"plot_id": "A"})

    result = process_draw(geo, name="area", gee=False)

    assert result.method == "DRAW"
    assert result.gee is False
    assert result.feature_collection is None
    assert result.admin is None
    assert len(result.gdf) == 1
    assert result.gdf.crs.to_epsg() == 4326
