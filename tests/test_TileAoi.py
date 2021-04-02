import unittest

import ee

from sepal_ui import aoi
from sepal_ui.message import ms

class TestAoiTile(unittest.TestCase):
    
    FOLDER = 'projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test'
    
    def test_FileName(self):
        
        file_name_field = aoi.FileNameField()
        
        self.assertIsInstance(file_name_field, aoi.FileNameField)
        
        return
    
    def test_admin_select(self):
        
        admin0_select = aoi.Adm0Select()
        admin1_select = aoi.Adm1Select()
        admin2_select = aoi.Adm2Select()
        
        self.assertIsInstance(admin0_select, aoi.Adm0Select)
        self.assertIsInstance(admin1_select, aoi.Adm1Select)
        self.assertIsInstance(admin2_select, aoi.Adm2Select)
        
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
        self.assertEqual(tile_aoi.aoi_output.children[1].children[0], ms.aoi_sel.no_selection)
        
        # launch with a coutry entry
        aoi_io.clear_attributes()
        tile_aoi.aoi_select_method.v_model = 'Country boundaries'
        tile_aoi.aoi_country_selection.v_model = 53
        tile_aoi.bind_aoi_process(tile_aoi.aoi_select_btn, None, None)
        
        self.assertEqual(aoi_io.adm0, 53)
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
        self.assertIn('d-none', tile_aoi.aoi_admin_1_select.class_)
        self.assertIn('d-none', tile_aoi.aoi_admin_2_select.class_)
        self.assertIn('d-none', tile_aoi.aoi_asset_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_load_table.class_)
        
        # admin 1
        tile_aoi.aoi_select_method.v_model = tile_aoi.SELECTION_METHOD[1]
        self.assertIn('d-none', tile_aoi.aoi_file_input.class_)
        self.assertIn('d-none', tile_aoi.aoi_file_name.class_)
        self.assertNotIn('d-none', tile_aoi.aoi_country_selection.class_)
        self.assertNotIn('d-none', tile_aoi.aoi_admin_1_select.class_)
        self.assertIn('d-none', tile_aoi.aoi_admin_2_select.class_)
        self.assertIn('d-none', tile_aoi.aoi_asset_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_load_table.class_)
        
        # admin 2
        tile_aoi.aoi_select_method.v_model = tile_aoi.SELECTION_METHOD[2]
        self.assertIn('d-none', tile_aoi.aoi_file_input.class_)
        self.assertIn('d-none', tile_aoi.aoi_file_name.class_)
        self.assertNotIn('d-none', tile_aoi.aoi_country_selection.class_)
        self.assertNotIn('d-none', tile_aoi.aoi_admin_1_select.class_)
        self.assertNotIn('d-none', tile_aoi.aoi_admin_2_select.class_)
        self.assertIn('d-none', tile_aoi.aoi_asset_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_load_table.class_)
        
        # select drawing 
        tile_aoi.aoi_select_method.v_model = tile_aoi.SELECTION_METHOD[3]
        self.assertIn('d-none', tile_aoi.aoi_file_input.class_)
        self.assertNotIn('d-none', tile_aoi.aoi_file_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_country_selection.class_)
        self.assertIn('d-none', tile_aoi.aoi_admin_1_select.class_)
        self.assertIn('d-none', tile_aoi.aoi_admin_2_select.class_)
        self.assertIn('d-none', tile_aoi.aoi_asset_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_load_table.class_)
        
        # select gee asset
        tile_aoi.aoi_select_method.v_model = tile_aoi.SELECTION_METHOD[4]
        self.assertIn('d-none', tile_aoi.aoi_file_input.class_)
        self.assertIn('d-none', tile_aoi.aoi_file_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_country_selection.class_)
        self.assertIn('d-none', tile_aoi.aoi_admin_1_select.class_)
        self.assertIn('d-none', tile_aoi.aoi_admin_2_select.class_)
        self.assertNotIn('d-none', tile_aoi.aoi_asset_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_load_table.class_)
        
        # select shp file
        tile_aoi.aoi_select_method.v_model = tile_aoi.SELECTION_METHOD[5]
        self.assertNotIn('d-none', tile_aoi.aoi_file_input.class_)
        self.assertNotIn('d-none', tile_aoi.aoi_file_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_country_selection.class_)
        self.assertIn('d-none', tile_aoi.aoi_admin_1_select.class_)
        self.assertIn('d-none', tile_aoi.aoi_admin_2_select.class_)
        self.assertIn('d-none', tile_aoi.aoi_asset_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_load_table.class_)
        
        # select point file
        tile_aoi.aoi_select_method.v_model = tile_aoi.SELECTION_METHOD[6]
        self.assertIn('d-none', tile_aoi.aoi_file_input.class_)
        self.assertNotIn('d-none', tile_aoi.aoi_file_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_country_selection.class_)
        self.assertIn('d-none', tile_aoi.aoi_admin_1_select.class_)
        self.assertIn('d-none', tile_aoi.aoi_admin_2_select.class_)
        self.assertIn('d-none', tile_aoi.aoi_asset_name.class_)
        self.assertNotIn('d-none', tile_aoi.aoi_load_table.class_)
        
        # select nothing 
        tile_aoi.aoi_select_method.v_model = None
        self.assertIn('d-none', tile_aoi.aoi_file_input.class_)
        self.assertIn('d-none', tile_aoi.aoi_file_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_country_selection.class_)
        self.assertIn('d-none', tile_aoi.aoi_admin_1_select.class_)
        self.assertIn('d-none', tile_aoi.aoi_admin_2_select.class_)
        self.assertIn('d-none', tile_aoi.aoi_asset_name.class_)
        self.assertIn('d-none', tile_aoi.aoi_load_table.class_)
        
        
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
    
    def test_on_file_change(self):
        
        # init 
        aoi_io = aoi.Aoi_io()
        tile_aoi = aoi.TileAoi(aoi_io, folder = self.FOLDER)
        
        # fake a file change
        fake_file = 'a_fake_file'
        tile_aoi._on_file_change({'new': fake_file})
        
        self.assertEqual(tile_aoi.aoi_file_name.v_model, fake_file)
        
        return 
    
    def test_on_table_change(self):
        
        # init 
        aoi_io = aoi.Aoi_io()
        tile_aoi = aoi.TileAoi(aoi_io, folder = self.FOLDER)
        
        # fake a table change
        fake_file = 'a_fake_file'
        fake_json = '{"pathname": "' + fake_file + '"}'
        tile_aoi._on_table_change({'new': fake_json})
        
        self.assertEqual(tile_aoi.aoi_file_name.v_model, fake_file)
        
        return 
        
if __name__ == '__main__':
    unittest.main()