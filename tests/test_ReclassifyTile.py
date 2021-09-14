from pathlib import Path

from sepal_ui import reclassify as rec
from sepal_ui.message import ms


class TestReclassifyTile:
    def test_init(self):

        # default init
        tile = rec.ReclassifyTile(Path.home(), gee=True)
        assert isinstance(tile, rec.ReclassifyTile)

        # init with ee
        tile = rec.ReclassifyTile(Path.home(), gee=False)
        assert tile.model.gee == False

        return
