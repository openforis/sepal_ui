git add .
import unittest
import os

import ee 

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import gee
from sepal_ui.message import ms

@unittest.skipIf('EE_DECRYPT_KEY' in os.environ, 'cannot be launched from a gservice account')
class TestGee(unittest.TestCase):
    
    DESCRIPTION = 'test_travis'
    ASSET_ID = 'users/bornToBeAlive/sepal_ui_test/{}'
    
    def test_wait_for_completion(self):
        
        # create an output alert 
        alert = sw.Alert()
        
        task = self._create_fake_task()
        
        res = gee.wait_for_completion(self.DESCRIPTION, alert)
        
        self.assertEqual(res, 'COMPLETED')
        self.assertEqual(alert.type, 'success')
        self.assertEqual(ms.status.format('COMPLETED'), alert.children[1].children[0])
        
        ee.data.deleteAsset(self.ASSET_ID.format(self.DESCRIPTION))
        
        #check that an error is raised when trying to overwrite a existing asset
        description = 'france'
        task = self._create_fake_task(description, False)
        
        with self.assertRaises(Exception): 
            res = gee.wait_for_completion(description, alert)
        
        return

    def test_is_task(self):
        
        # create an output alert 
        alert = sw.Alert()
        
        task = self._create_fake_task()
        
        # wait for the task to finish 
        gee.wait_for_completion(self.DESCRIPTION, alert)
        
        # check if it exist
        res = gee.is_task(self.DESCRIPTION)
        
        self.assertNotEqual(res, None)
        
        # delete the asset 
        ee.data.deleteAsset(self.ASSET_ID.format(self.DESCRIPTION))
        
        return
    
    def test_get_assets(self):
        
        # get the assets from the test repository 
        folder = 'projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test'
        list_ = gee.get_assets(folder)
        
        # check that they are all there 
        names = ['corsica_template', 'france', 'italy']
        
        for item, name in zip(list_, names):
            self.assertEqual(item['name'], f'{folder}/{name}')
            
        return
    
    def test_isAsset(self):
        
        folder = 'projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test'
        
        # real asset 
        res = gee.is_asset(f'{folder}/france', folder)
        self.assertTrue(res)
        
        # fake asset 
        res = gee.is_asset(f'{folder}/toto', folder)
        self.assertFalse(res)
        
        return
    
    def _create_fake_task(self, description = DESCRIPTION, delete = True):
        
        # create a fake exportation task 
        point = ee.FeatureCollection(ee.Geometry.Point([1.5, 1.5]))
        task_config = {
            'collection': point, 
            'description': description,
            'assetId': self.ASSET_ID.format(description)
        }
        task = ee.batch.Export.table.toAsset(**task_config)
        task.start()
        
        return task
        
if __name__ == '__main__':
    unittest.main()