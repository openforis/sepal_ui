import ee

from sepal_ui import aoi
from sepal_ui.message import ms


class TestAoiTile:

    FOLDER = "projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test"

    def test_init(self):

        # default init
        tile = aoi.AoiTile(folder=self.FOLDER)
        assert isinstance(tile, aoi.AoiTile)

        # init without ee
        tile = aoi.AoiTile(folder=self.FOLDER, gee=False)
        assert tile.view.model.ee == False

        return
