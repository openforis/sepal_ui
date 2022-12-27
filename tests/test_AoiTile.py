import ee
import pytest

from sepal_ui import aoi


class TestAoiTile:
    def test_init(self):

        # init without ee
        tile = aoi.AoiTile(gee=False)
        assert isinstance(tile, aoi.AoiTile)
        assert tile.view.model.gee is False

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_init_ee(self, gee_dir):

        # default init
        tile = aoi.AoiTile(folder=str(gee_dir))
        assert isinstance(tile, aoi.AoiTile)
        assert tile.view.model.gee is True

        return
