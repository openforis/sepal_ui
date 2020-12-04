import unittest

import ee

from sepal_ui import aoi
from sepal_ui.scripts import messages as ms

class TestAoiTile(unittest.TestCase):
    
    FOLDER = 'projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test'
    
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
        tile = aoi.TileAoi(aoi_io, folder = self.FOLDER)
        
        self.assertIsInstance(tile, aoi.TileAoi)        
        
        return
    
    def test_bind_aoi_process(self):
        
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        aoi_io = aoi.Aoi_io(default_asset = asset_id)
        tile_aoi = aoi.TileAoi(aoi_io, folder = self.FOLDER)
        
        # launch the click without any entry 
        tile_aoi.bind_aoi_process(tile_aoi.aoi_select_btn, None, None)
        self.assertEqual(tile_aoi.output.children[0].children[0], ms.NO_SELECTION)
        
        # launch with a coutry entry
        aoi_io.clear_attributes()
        tile_aoi.aoi_select_method.v_model = 'Country boundaries'
        tile_aoi.aoi_country_selection.v_model = 'France'
        tile_aoi.bind_aoi_process(tile_aoi.aoi_select_btn, None, None)
        
        self.assertEqual(aoi_io.country_selection, 'France')
        self.assertNotEqual(aoi_io.feature_collection, None)
        
        # launch with a gee asset
        aoi_io.clear_attributes()
        tile_aoi.aoi_select_method.v_model = 'Use GEE asset'
        tile_aoi.aoi_asset_name.v_model = asset_id
        tile_aoi.bind_aoi_process(tile_aoi.aoi_select_btn, None, None)
        
        self.assertEqual(aoi_io.assetId, asset_id)
        
        return 
    
    def test_bind_aoi_method(self):
        
        aoi_io = aoi.Aoi_io()
        tile_aoi = aoi.TileAoi(aoi_io, folder = self.FOLDER)
        
        # select country selection 
        tile_aoi.aoi_select_method.v_model = tile_aoi.SELECTION_METHOD[0]
        self.assertIn('d-none', tile_aoi.aoi_file_input.class_)
        self.assertIn('d-none', tile_aoi.aoi_file_name.class_)
        self.assertNotIn('d-none', tile_aoi.aoi_country_selection.class_)
        self.assertIn('d-none', tile_aoi.aoi_asset_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_load_table.class_)
        
        # select drawing 
        tile_aoi.aoi_select_method.v_model = tile_aoi.SELECTION_METHOD[1]
        self.assertIn('d-none', tile_aoi.aoi_file_input.class_)
        self.assertNotIn('d-none', tile_aoi.aoi_file_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_country_selection.class_)
        self.assertIn('d-none', tile_aoi.aoi_asset_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_load_table.class_)
        
        # select shp file
        tile_aoi.aoi_select_method.v_model = tile_aoi.SELECTION_METHOD[2]
        self.assertNotIn('d-none', tile_aoi.aoi_file_input.class_)
        self.assertIn('d-none', tile_aoi.aoi_file_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_country_selection.class_)
        self.assertIn('d-none', tile_aoi.aoi_asset_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_load_table.class_)
        
        # select gee asset
        tile_aoi.aoi_select_method.v_model = tile_aoi.SELECTION_METHOD[3]
        self.assertIn('d-none', tile_aoi.aoi_file_input.class_)
        self.assertIn('d-none', tile_aoi.aoi_file_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_country_selection.class_)
        self.assertNotIn('d-none', tile_aoi.aoi_asset_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_load_table.class_)
        
        # select point file
        tile_aoi.aoi_select_method.v_model = tile_aoi.SELECTION_METHOD[4]
        self.assertIn('d-none', tile_aoi.aoi_file_input.class_)
        self.assertIn('d-none', tile_aoi.aoi_file_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_country_selection.class_)
        self.assertIn('d-none', tile_aoi.aoi_asset_name.class_)
        self.assertNotIn('d-none', tile_aoi.aoi_load_table.class_)
        
        return 
    
    def test_handle_draw(self):
        
        aoi_io = aoi.Aoi_io()
        tile_aoi = aoi.TileAoi(aoi_io, folder = self.FOLDER)
        
        # test data 
        geojson = {
            'type': 'Feature', 
            'properties': {
                'style': {
                    'stroke': True, 
                    'color': '#79B1C9', 
                    'weight': 4, 
                    'opacity': 0.5, 
                    'fill': True, 
                    'fillColor': None, 
                    'fillOpacity': 0.2, 
                    'clickable': True
                }
            }, 
            'geometry': {
                'type': 'Polygon', 
                'coordinates': [
                    [[8.440211, 41.362895], 
                    [8.440211, 42.991088], 
                    [9.670726, 42.991088], 
                    [9.670726, 41.362895], 
                    [8.440211, 41.362895]]
                ]
            }
        }
        
        tile_aoi.handle_draw(tile_aoi.m, None, geojson)
        
        self.assertIsInstance(aoi_io.drawn_feat, ee.FeatureCollection)
        
        return       
        
if __name__ == '__main__':
    unittest.main()