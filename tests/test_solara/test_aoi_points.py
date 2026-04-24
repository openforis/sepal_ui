"""Tests for process_points."""

import asyncio
from pathlib import Path

import pytest

from pysepal.solara.components.aoi.points import process_points

DATA = Path(__file__).resolve().parents[1] / "data" / "aoi_manual"
CSV = DATA / "manual_points.csv"
SEMICOLON = DATA / "manual_points_semicolon.txt"


def _run(coro):
    return asyncio.run(coro)


def test_process_points_rejects_empty_path():
    with pytest.raises(ValueError):
        _run(
            process_points(
                "", id_column="site_id", lat_column="latitude", lng_column="longitude", gee=False
            )
        )


def test_process_points_requires_all_columns():
    with pytest.raises(ValueError):
        _run(
            process_points(
                str(CSV), id_column="", lat_column="latitude", lng_column="longitude", gee=False
            )
        )


def test_process_points_rejects_duplicate_columns():
    with pytest.raises(ValueError, match="Duplicate column"):
        _run(
            process_points(
                str(CSV),
                id_column="latitude",
                lat_column="latitude",
                lng_column="longitude",
                gee=False,
            )
        )


def test_process_points_rejects_missing_columns():
    with pytest.raises(ValueError, match="Columns not found"):
        _run(
            process_points(
                str(CSV),
                id_column="site_id",
                lat_column="lat_missing",
                lng_column="longitude",
                gee=False,
            )
        )


def test_process_points_loads_csv():
    result = _run(
        process_points(
            str(CSV),
            id_column="site_id",
            lat_column="latitude",
            lng_column="longitude",
            gee=False,
        )
    )

    assert result.method == "POINTS"
    assert result.gee is False
    assert result.feature_collection is None
    assert result.gdf.crs.to_epsg() == 4326
    assert len(result.gdf) == 4
    assert (result.gdf.geometry.geom_type == "Point").all()
    # Longitude/latitude columns must map to x/y of the Point geometry.
    first_row = result.gdf.iloc[0]
    assert first_row.geometry.x == pytest.approx(first_row["longitude"])
    assert first_row.geometry.y == pytest.approx(first_row["latitude"])


def test_process_points_autodetects_semicolon_separator():
    result = _run(
        process_points(
            str(SEMICOLON),
            id_column="plot_id",
            lat_column="lat",
            lng_column="lng",
            gee=False,
        )
    )

    # pandas with sep=None sniffs the separator; if this breaks, the loader regressed.
    assert len(result.gdf) == 3
    assert "plot_id" in result.gdf.columns
