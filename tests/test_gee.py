import unittest
import os

import ee 

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import gee
from sepal_ui.scripts import messages as ms

@unittest.skipIf('EE_PRIVATE_KEY' in os.environ, 'cannot be launched from a gservice account')
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
        self.assertEqual(ms.STATUS.format('COMPLETED'), alert.children[1].children[0])
        
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
        res = gee.isTask(self.DESCRIPTION)
        
        self.assertNotEqual(res, None)
        
        # delete the asset 
        ee.data.deleteAsset(self.ASSET_ID.format(self.DESCRIPTION))
        
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