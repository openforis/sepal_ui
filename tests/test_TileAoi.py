import unittest

from sepal_ui import aoi

class TestAoiTile(unittest.TestCase):
    
    def test_FileName(self):
        
        file_name_field = aoi.FileNameField()
        
        self.assertIsInstance(file_name_field, aoi.FileNameField)
        
        return
    
    def test_country_select(self):
        
        country_select = aoi.CountrySelect()
        
        self.assertIsInstance(country_select, aoi.CountrySelect)
        
        return

    def test_init(self):
        
        aoi_io = aoi.Aoi_io()
        
        #default init
        tile = aoi.TileAoi(aoi_io)
        
        self.assertIsInstance(tile, aoi.TileAoi)        
        
        return
    
    def test_bind_aoi_process(self):
        
        # launch the click without any entry 
        
        # launch with a coutry entry 
        
        return 
    
    def test_bind_aoi_method(self):
        
        # select country selection 
        
        # select drawing 
        
        # select shp file
        
        # select gee asset
        
        # select point file
        
        return 

if __name__ == '__main__':
    unittest.main()