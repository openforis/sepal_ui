from sepal_ui import aoi


class TestAoiTile:
    def test_init(self, gee_dir):

        # default init
        tile = aoi.AoiTile(folder=gee_dir)
        assert isinstance(tile, aoi.AoiTile)

        # init without ee
        tile = aoi.AoiTile(gee=False)
        assert tile.view.model.ee is False

        return
