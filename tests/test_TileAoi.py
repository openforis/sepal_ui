import unittest

from sepal_ui import aoi

class TestAoiTile(unittest.TestCase):

    def test_init(self):
        
        aoi_io = aoi.Aoi_io()
        
        #default init
        tile = aoi.TileAoi(aoi_io)
        
        self.assertIsInstance(tile, aoi.TileAoi)        
        
        return
        
if __name__ == '__main__':
    unittest.main()