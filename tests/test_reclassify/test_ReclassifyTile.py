"""Test the ReclassifyTile widget"""

from pathlib import Path

import ee
import pytest

from sepal_ui import reclassify as rec


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_init_gee(gee_dir: Path) -> None:
    """Check widget init with GEE

    Args:
        gee_dir: session created GEE directory
    """

    # default init
    tile = rec.ReclassifyTile(Path.home(), gee=True, folder=gee_dir)
    assert isinstance(tile, rec.ReclassifyTile)

    return


def test_init() -> None:
    """Check widget init without GEE"""

    # init without ee
    tile = rec.ReclassifyTile(Path.home(), gee=False)
    assert tile.model.gee is False

    return
