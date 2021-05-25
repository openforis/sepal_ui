import unittest

import ee

from sepal_ui import aoi
from sepal_ui.message import ms

class TestAoiTile(unittest.TestCase):
    
    FOLDER = 'projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test'

    def test_init(self):
        
        # default init
        tile = aoi.AoiTile(folder = self.FOLDER)
        self.assertIsInstance(tile, aoi.AoiTile)    
        
        # init with ee 
        tile = aoi.AoiTile(folder= self.FOLDER, gee=False)
        self.assertFalse(tile.view.model.ee)
        
        return
        
if __name__ == '__main__':
    unittest.main()