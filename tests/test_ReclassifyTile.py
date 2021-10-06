from pathlib import Path

from sepal_ui import reclassify as rec
from sepal_ui.message import ms


class TestReclassifyTile:
    def test_init(self, gee_dir):

        # default init
        tile = rec.ReclassifyTile(Path.home(), gee=True, folder=gee_dir)
        assert isinstance(tile, rec.ReclassifyTile)

        # init without ee
        tile = rec.ReclassifyTile(Path.home(), gee=False)
        assert tile.model.gee == False

        return
