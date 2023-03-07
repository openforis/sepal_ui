"""Test AoiTile widget."""

from pathlib import Path

import ee
import pytest

from sepal_ui import aoi


def test_init() -> None:
    """Init an AoiTile without GEE."""
    # init without ee
    tile = aoi.AoiTile(gee=False)
    assert isinstance(tile, aoi.AoiTile)
    assert tile.view.model.gee is False

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_init_ee(gee_dir: Path) -> None:
    """Init an AoiTile with GEE.

    Args:
        gee_dir: path to the session gee directory where assets are saved
    """
    # default init
    tile = aoi.AoiTile(folder=str(gee_dir))
    assert isinstance(tile, aoi.AoiTile)
    assert tile.view.model.gee is True

    return
