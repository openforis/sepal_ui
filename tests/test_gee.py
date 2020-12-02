import unittest

import ee 

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su
from sepal_ui.scripts import gee

su.init_ee()

@unittest.skip("points are not exported, GEE API problem as usual")
class TestAlert(unittest.TestCase):
    
    def test_wait_for_completion(self):
        
        # create an output alert 
        alert = sw.Alert()
        
        # create a fake exportation task 
        description = 'test_travis'
        asset_id = f'users/bornToBeAlive/sepal_ui_test/{description}'
        point = ee.Geometry.Point([1.5, 1.5])
        task_config = {
            'collection': point, 
            'description': description,
            'assetId': asset_id
        }
        task = ee.batch.Export.table.toAsset(**task_config)
        task.start()
        res = gee.wait_for_completion(description, alert)
        
        self.assertEqual(res, 'COMPLETED')
        self.assertEqual(alert.type, 'success')
        self.assertEqual(res, alert.children[1].children[0])
        
        # remove the asset 
        ee.data.deleteAsset(asset_id)
        
        return 
    
    def test_is_task(self):
        
        # create a fake exportation task 
        description = 'test_travis'
        asset_id = f'users/bornToBeAlive/sepal_ui_test/{description}'
        point = ee.Geometry.Point([1.5, 1.5])
        task_config = {
            'collection': point, 
            'description': description,
            'assetId': f'users/bornToBeAlive/sepal_ui_test/{description}'
        }
        task = ee.batch.Export.table.toAsset(**task_config)
        task.start()
        
        # wait for the task to finish 
        gee.wait_for_completion(description, alert)
        
        # check if it exist
        res = gee.isTask(description)
        
        self.assertNotEqual(res, None)
        
        # delete the asset 
        ee.data.deleteAsset(asset_id)
        
        return
        
if __name__ == '__main__':
    unittest.main()