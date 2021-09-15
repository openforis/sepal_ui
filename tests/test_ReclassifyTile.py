from pathlib import Path

from sepal_ui import reclassify as rec
from sepal_ui.message import ms


class TestReclassifyTile:
    
    FOLDER = "projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test"
    
    def test_init(self):

        # default init
        tile = rec.ReclassifyTile(Path.home(), gee=True, folder=self.FOLDER)
        assert isinstance(tile, rec.ReclassifyTile)

        # init without ee
        tile = rec.ReclassifyTile(Path.home(), gee=False)
        assert tile.model.gee == False

        return
