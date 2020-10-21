import unittest

import ipyvuetify as v

from sepal_ui import aoi as sw

class TestFooter(unittest.TestCase):
    
    def test_init(self):
        
        aoi_io = sw.Aoi_io()
        
        #default init
        tile = sw.TileAoi(aoi_io)
        
        self.assertIsInstance(tile, sw.TileAoi)        
        
        return
        
if __name__ == '__main__':
    unittest.main()