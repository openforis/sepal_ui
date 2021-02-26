import unittest
import ee
from pathlib import Path

from sepal_ui import aoi
from sepal_ui import mapping as sm

class TestAoi_io(unittest.TestCase):
    
    def test_init(self):
        
        # default init
        aoi_io = aoi.Aoi_io()
        
        self.assertIsInstance(aoi_io, aoi.Aoi_io)
        self.assertEqual(aoi_io.assetId, None)
        
        # with default assetId 
        asset_id = 'users/username/assetID'
        aoi_io = aoi.Aoi_io(default_asset = asset_id)
        
        self.assertEqual(aoi_io.assetId, asset_id)
        
        # with a default admin 
        admin = 53
        aoi_io = aoi.Aoi_io(default_admin0 = admin)
        
        self.assertNotEqual(aoi_io.feature_collection, None)
        
        return 
    
    def test_get_aoi_ee(self):
        
        # init 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        ee_france = ee.FeatureCollection(asset_id)
        ee_italy = ee.FeatureCollection('users/bornToBeAlive/sepal_ui_test/italy')
        
        # an aoi with an assetId  
        aoi_io = aoi.Aoi_io(default_asset = asset_id)
        ee_obj = aoi_io.get_aoi_ee()
        
        self.assertEqual(ee_obj, ee_france)
        
        # fake an administrative country 
        aoi_io.country_code = 53 # fake number to force is_admin to return true
        aoi_io.feature_collection = ee_italy
        ee_obj = aoi_io.get_aoi_ee()
        
        obj_id = ee_obj.getInfo()['id']
        italy_id = ee_italy.getInfo()['id']
        self.assertEqual(obj_id, italy_id)
        
        return
    
    def test_get_columns(self):
        
        # init 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        aoi_io = aoi.Aoi_io(default_asset = asset_id)
        
        # test data 
        test_data = [
            'ADM0_CODE',
            'ADM0_NAME',
            'DISP_AREA',
            'EXP0_YEAR',
            'STATUS',
            'STR0_YEAR',
            'Shape_Leng'
        ]
        
        res = aoi_io.get_columns()
        
        self.assertEqual(res, test_data)
        
        return 
    
    def test_get_fields(self):
        
        # init 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        aoi_io = aoi.Aoi_io(default_asset = asset_id)
        column = 'ADM0_CODE'
        
        res = aoi_io.get_fields(column)
        
        self.assertEqual(res, [85])
        
        # use a self defined column 
        aoi_io.column = column
        res = aoi_io.get_fields()
        
        self.assertEqual(res, [85])
        
        return
    
    def test_get_selected_feature(self):
        
        # init 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        aoi_io = aoi.Aoi_io(default_asset = asset_id)
        ee_france = ee.FeatureCollection(asset_id)
        
        # select the geometry associated with france (all of it)
        aoi_io.column = 'ADM0_CODE'
        aoi_io.field = 85
        
        feature = aoi_io.get_selected_feature()
        
        feature_geom = feature.getInfo()
        france_geom = ee_france.geometry().getInfo()
        
        self.assertEqual(feature_geom, france_geom)
        
        # crash it with an empty col and field 
        aoi_io.clear_attributes()
        
        with self.assertRaises(Exception): 
            feature = aoi_io.get_selected_feature()
        
        return 
    
    def test_clear_selected(self):
        
        aoi_io = aoi.Aoi_io()
        aoi_io.selected_feature = 2
        
        aoi_io.clear_selected()
        
        self.assertEqual(aoi_io.selected_feature, None)
        
        return 
    
    def test_clear_attributes(self):
        
        aoi_io = aoi.Aoi_io()
        
        dum = "dum"
        
        # instret dum parameter everywhere 
        aoi_io.column = dum
        aoi_io.field = dum
        aoi_io.selected_feature = dum
        aoi_io.json_csv = dum
        aoi_io.country_code = dum
        aoi_io.feature_collection = dum
        aoi_io.file_input = dum
        aoi_io.file_name = dum
        aoi_io.country_selection = dum
        aoi_io.selection_method = dum
        aoi_io.drawn_feat = dum
        
        # clear them
        aoi_io.clear_attributes()
        
        self.assertEqual(aoi_io.column, None)
        self.assertEqual(aoi_io.field, None)
        self.assertEqual(aoi_io.selected_feature, None)
        self.assertEqual(aoi_io.json_csv, None)
        self.assertEqual(aoi_io.country_code, None)
        self.assertEqual(aoi_io.feature_collection, None)
        self.assertEqual(aoi_io.file_input, None)
        self.assertEqual(aoi_io.file_name, None)
        self.assertEqual(aoi_io.country_selection, None)
        self.assertEqual(aoi_io.selection_method, None)
        self.assertEqual(aoi_io.drawn_feat, None)

        return 
    
    def test_get_not_null_attrs(self):
        
        aoi_io = aoi.Aoi_io()
        
        attrs = aoi_io.get_not_null_attrs()
        
        self.assertEqual(len(attrs), 0)
        
        return 
    
    def test_display_on_map(self):
        
        # init 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        aoi_io = aoi.Aoi_io(default_asset = asset_id)
        m = sm.SepalMap()
        
        aoi_io.display_on_map(m)
        
        self.assertEqual(m.layers[1].name, 'aoi')
        self.assertEqual(m.zoom, 5.)
        self.assertEqual(m.center, [46.5135930048161, 2.574509802526499])
        
    def test_get_bounds(self):
        
        # init 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        aoi_io = aoi.Aoi_io(default_asset = asset_id)
        
        # test data 
        expected_cardinals = (
            (-5.142230921252722, 51.09281241936492),
            (-5.142230921252722, 41.33878298628808),
            (9.561552263332496, 51.09281241936492),
            (9.561552263332496, 41.33878298628808)
        )
        expected_bounds = (
            -5.142230921252722, 
            41.33878298628808, 
            9.561552263332496, 
            51.09281241936492
        )
        
        cardinals = aoi_io.get_bounds(aoi_io.assetId, True)
        bounds = aoi_io.get_bounds(aoi_io.assetId)
        
        self.assertEqual(cardinals, expected_cardinals)
        self.assertEqual(bounds, expected_bounds)
        
        return
    
    def test_get_aoi_shp(self):
        
        # init 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        aoi_io = aoi.Aoi_io(default_asset = asset_id)
        out_dir = Path('~').expanduser()
        
        filename = aoi_io.get_aoi_shp(out_dir)
        
        self.assertEqual(filename, out_dir.joinpath('france.shp'))
        self.assertEqual(Path(filename).stat().st_size, 236)
        
        #check if the filename is return when already exist
        filename = aoi_io.get_aoi_shp(out_dir)
        
        self.assertEqual(filename, out_dir.joinpath('france.shp'))
        
        # remove the files 
        for f in out_dir.glob('france.*'):
            f.unlink()
        
        return 
    
    def test_get_aoi_name(self):
        
        # init 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        aoi_io = aoi.Aoi_io(default_asset = asset_id)
        
        name = aoi_io.get_aoi_name()
        self.assertEqual(name, 'france')
        
        # use a country code 
        code = 'FRA'
        aoi_io.country_code = code
        name = aoi_io.get_aoi_name()
        self.assertEqual(name, code)
        
        return 
    
if __name__ == '__main__':
    unittest.main()