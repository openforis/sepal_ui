import unittest
from unittest.mock import patch
from pathlib import Path
import json
from glob import glob

import ee

import sepal_ui
from sepal_ui import sepalwidgets as sw
from sepal_ui import aoi
from sepal_ui.scripts import utils as su
from sepal_ui.scripts import messages as ms
from sepal_ui.scripts.run_aoi_selection import * 

su.init_ee()

class TestRunAoiSelection(unittest.TestCase):
    
    def test_isAsset(self):
        
        folder = 'projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test'
        
        # real asset 
        res = isAsset('france', folder)
        self.assertTrue(res)
        
        # fake asset 
        res = isAsset('toto', folder)
        self.assertFalse(res)
        
        return 
    
    def test_country_asset(self):
        
        alert = sw.Alert()
        
        country, iso_3 = get_country_asset('France', alert)
        
        column = 'ADM0_NAME'
        name =country.distinct(column).aggregate_array(column).getInfo()[0]
        self.assertEqual(name, 'France')
        self.assertEqual(iso_3, 'FRA')
    
        return 
    
    @unittest.skipIf('EE_PRIVATE_KEY' in os.environ, 'cannot be launched from a gservice account')
    def test_get_drawn_shape(self):
        
        alert = sw.Alert()
        
        folder = 'projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test'
        
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
        
        geom = geemap.geojson_to_ee(geojson, False)
        feature = ee.Feature(geom)
        ee_feature = ee.FeatureCollection(feature)
        
        # send no drawn_feat 
        asset = get_drawn_shape(None, 'corsica', folder, alert)
        self.assertFalse(asset)
        self.assertEqual(alert.children[0].children[0], ms.NO_SHAPE)
        
        # send the drawn feat to EE
        corsica = get_drawn_shape(ee_feature, 'corsica', folder, alert)
        name = Path(corsica).stem
        self.assertTrue(isAsset(name, folder))
        
        # send no already existing
        asset = get_drawn_shape(ee_feature, 'corsica', folder, alert)
        self.assertFalse(asset)
        self.assertEqual(alert.children[0].children[0], ms.NAME_USED)
        
        ee.data.deleteAsset(corsica)
        
        return
    
    def test_get_gee_Asset(self):
        
        alert = sw.Alert()
        
        # check with nothing 
        asset = get_gee_asset('', alert)
        self.assertFalse(asset)
        self.assertEqual(alert.children[0].children[0], ms.NO_ASSET)
        
        # check with a real asset 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        asset = get_gee_asset(asset_id, alert)
        self.assertEqual(asset, asset_id)
        self.assertEqual(alert.children[0].children[0], ms.CHECK_IF_ASSET)
        
        return 
    
    @unittest.skipIf('EE_PRIVATE_KEY' in os.environ, 'cannot be launched from a gservice account')
    def test_get_csv_asset(self):
        
        folder = 'projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test'
        
        alert = sw.Alert()
        
        # create the fake file
        filename = self._create_fake_table()
        
        # launch one with duplicate keys
        json_csv = json.dumps({
            "pathname": filename, 
            "id_column": "id", 
            "lat_column": "lat",
            "lng_column": "lat"
        })
        
        asset = get_csv_asset(json_csv, folder, alert)
        self.assertFalse(asset)
        self.assertEqual(alert.children[0].children[0], ms.DUPLICATE_KEY)
        
        # launch with a real asset
        json_csv = json.dumps({
            "pathname": filename, 
            "id_column": "id", 
            "lat_column": "lat",
            "lng_column": "lng"
        })
        
        asset = get_csv_asset(json_csv, folder, alert)
        self.assertEqual(asset, f'{folder}/aoi_test')
        
        ee.data.deleteAsset(asset)
        
        return
    
    @unittest.skipIf('EE_PRIVATE_KEY' in os.environ, 'cannot be launched from a gservice account')
    def test_shp_aoi(self):
        
        alert = sw.Alert()
        
        folder = 'projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test'
        
        # create the shape file from gee france asset 
        asset_id = 'users/bornToBeAlive/sepal_ui_test/france'
        aoi_io = aoi.Aoi_io(default_asset = asset_id)
        out_dir = os.path.expanduser('~')
        filename = aoi_io.get_aoi_shp(out_dir)
        
        name_ext = '_test'
        for file in glob(str(Path(filename).with_suffix('.*'))):
            new_name = str(Path(file).with_suffix('')) + name_ext + Path(file).suffix
            os.rename(file, new_name)
            
        filename = str(Path(file).with_suffix('')) + name_ext + Path(filename).suffix
        
        # load the shp in gee 
        asset = get_shp_aoi(filename, folder, alert)
        self.assertEqual(asset, f'{folder}/aoi_france_test')
        
        # remove the files 
        for file in glob(str(Path(filename).with_suffix('.*'))):
            os.remove(file)
            
        # delete the asset 
        ee.data.deleteAsset(asset)
        
        return
    @unittest.skip('mock function does not find the sepal_ui module')
    def test_run_aoi_selection(self):
        
        alert = sw.Alert()
        aoi_io = aoi.Aoi_io()
        methods = aoi.TileAoi.SELECTION_METHOD
        
        # with no method 
        run_aoi_selection(alert, None, aoi_io)
        self.assertEqual(alert.children[0].children[0], ms.NO_SELECTION)
        
        # mock country asset 
        with patch(' sepal_ui.scripts.run_aoi_selection.get_country_asset'):
            run_aoi_selection(alert, method[0], aoi_io)
            self.assertTrue(get_country_asset.assert_called_once())
            
        # mock drawn shape
        with patch(' sepal_ui.scripts.run_aoi_selection.get_drawn_shape'):
            run_aoi_selection(alert, method[1], aoi_io)
            self.assertTrue(get_drawn_shape.assert_called_once())
            
        # mock gee asset
        with patch(' sepal_ui.scripts.run_aoi_selection.get_gee_asset'):
            run_aoi_selection(alert, method[3], aoi_io)
            self.assertTrue(get_gee_asset.assert_called_once())
            
        # mock shapefile
        with patch(' sepal_ui.scripts.run_aoi_selection.get_shp_aoi'):
            run_aoi_selection(alert, method[2], aoi_io)
            self.assertTrue(get_shp_aoi.assert_called_once())
            
        # mock csv files
        with patch(' sepal_ui.scripts.run_aoi_selection.get_csv_asset'):
            run_aoi_selection(alert, method[4], aoi_io)
            self.assertTrue(get_csv_asset.assert_called_once())
            
        return
    
    def _create_fake_table(self):
        
        root_dir = os.path.expanduser('~')
        filename = f'{root_dir}/test.csv'
        
        coloseo = [1, 41.89042582290999, 12.492241627092199]
        fao = [2, 41.88369224629387, 12.489216069409004]
        df = pd.DataFrame([coloseo, fao], columns=['id', 'lat', 'lng'])
        
        df.to_csv(filename, index = False)
        
        return filename 

if __name__ == '__main__':
    unittest.main()