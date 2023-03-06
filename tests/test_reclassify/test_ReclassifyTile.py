from pathlib import Path

import ee
import pytest

from sepal_ui import reclassify as rec


class TestReclassifyTile:
    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_init_gee(self, gee_dir):

        # default init
        tile = rec.ReclassifyTile(Path.home(), gee=True, folder=gee_dir)
        assert isinstance(tile, rec.ReclassifyTile)

        return

    def test_init(self):

        # init without ee
        tile = rec.ReclassifyTile(Path.home(), gee=False)
        assert tile.model.gee is False

        return
