import unittest
import ee
from pathlib import Path

from sepal_ui import aoi
from sepal_ui import sepalwidgets as sw 

class TestAoiModel(unittest.TestCase):
    
    def test_init(self):
        
        # dummy alert 
        alert = sw.Alert()
        
        # default init
        aoi_model = aoi.AoiModel(alert)
        self.assertIsInstance(aoi_model, aoi.AoiModel)
        self.assertEqual(aoi_model.ee, True)
        
        # with default assetId 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/italy'
        aoi_model = aoi.AoiModel(alert, asset = asset_id)
        
        self.assertEqual(aoi_model.asset_name, asset_id)
        self.assertEqual(aoi_model.default_asset, asset_id)
        self.assertNotEqual(all(aoi_model.gdf), None)
        self.assertNotEqual(aoi_model.feature_collection, None)
        self.assertEqual(aoi_model.name, 'italy')
        
        # with a default admin 
        admin =  85 # GAUL France
        aoi_model = aoi.AoiModel(alert, admin=admin)
        
        self.assertEqual(aoi_model.name, 'FRA')
        
        # test with a non ee definition 
        admin = 'FRA' # GADM France
        aoi_model = aoi.AoiModel(alert, gee=False, admin=admin)
        
        self.assertEqual(aoi_model.name, 'FRA')
        
        return
    
    def test_get_columns(self):
        
        # dummy alert 
        alert = sw.Alert()
        
        # init 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        aoi_model = aoi.AoiModel(alert, asset=asset_id)
        
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
        
        res = aoi_model.get_columns()
        
        self.assertEqual(res, test_data)
        
        return 
    
    def test_get_fields(self):
        
        # dummy alert 
        alert = sw.Alert()
        
        # init 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        aoi_model = aoi.AoiModel(alert, asset = asset_id)
        column = 'ADM0_CODE'
        
        res = aoi_model.get_fields(column)
        
        self.assertEqual(res, [85])
        
        return
    
    def test_get_selected(self):
        
        # dummy alert 
        alert = sw.Alert()
        
        # init 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        aoi_model = aoi.AoiModel(alert, asset = asset_id)
        ee_france = ee.FeatureCollection(asset_id)
        
        # select the geometry associated with france (all of it)
        column = 'ADM0_CODE'
        field = 85
        
        feature = aoi_model.get_selected(column, field)
        
        feature_geom = feature.geometry().getInfo()
        france_geom = ee_france.geometry().getInfo()
        
        self.assertEqual(feature_geom, france_geom)
        
        return  
    
    def test_clear_attributes(self):
        
        # dummy alert 
        alert = sw.Alert()
        
        aoi_model = aoi.AoiModel(alert)
        
        dum = "dum"
        
        # insert dum parameter everywhere 
        aoi_model.method = dum 
        aoi_model.point_json = dum
        aoi_model.vector_json = dum
        aoi_model.geo_json = dum
        aoi_model.admin = dum
        aoi_model.asset_name = dum 
        aoi_model.name = dum
        aoi_model.gdf = dum
        aoi_model.feature_collection = dum 
        aoi_model.ipygeojson = dum
        
        # clear them
        aoi_model.clear_attributes()
        
        self.assertEqual(aoi_model.method             , None) 
        self.assertEqual(aoi_model.point_json         , None)
        self.assertEqual(aoi_model.vector_json        , None)
        self.assertEqual(aoi_model.geo_json           , None)
        self.assertEqual(aoi_model.admin              , None)
        self.assertEqual(aoi_model.asset_name         , None) 
        self.assertEqual(aoi_model.name               , None)
        self.assertEqual(aoi_model.gdf                , None)
        self.assertEqual(aoi_model.feature_collection , None) 
        self.assertEqual(aoi_model.ipygeojson         , None)
        self.assertEqual(aoi_model.default_asset      , None) 
        self.assertEqual(aoi_model.default_admin      , None)
        self.assertEqual(aoi_model.default_vector     , None) 
        
        # check that default are saved 
        aoi_model = aoi.AoiModel(alert, admin=85) # GAUL for France
        
        # insert dummy args
        aoi_model.method = dum 
        aoi_model.point_json = dum
        aoi_model.vector_json = dum
        aoi_model.geo_json = dum
        aoi_model.admin = dum
        aoi_model.asset_name = dum 
        aoi_model.name = dum
        aoi_model.gdf = dum
        aoi_model.feature_collection = dum 
        aoi_model.ipygeojson = dum 
        
        # clear 
        aoi_model.clear_attributes()
        
        # assert that it's still france 
        self.assertEqual(aoi_model.name, 'FRA')
        
        return 

        
    def test_total_bounds(self):
        
        # dummy alert 
        alert = sw.Alert()
        
        # init 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        aoi_model = aoi.AoiModel(alert, asset = asset_id)
        
        # test data 
        expected_bounds = (
            -5.142230921252722, 
            41.33878298628808, 
            9.561552263332496, 
            51.09281241936492
        )
        
        bounds = aoi_model.total_bounds()
        
        self.assertEqual(bounds, expected_bounds)
        
        return
    
if __name__ == '__main__':
    unittest.main()