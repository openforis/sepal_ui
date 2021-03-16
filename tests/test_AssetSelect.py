import unittest

import ee

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su

class TestAssetSelect(unittest.TestCase):
    
    def test_init(self):
        
        # create an asset select that points to the foder I created for testing
        folder = 'projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test'
        std_root = folder.replace('projects/earthengine-legacy/assets/', '')
        asset_select = sw.AssetSelect(folder = folder)
        
        self.assertIsInstance(asset_select, sw.AssetSelect)
        self.assertIn(f'{std_root}/france', asset_select.items)
        
        return
        
if __name__ == '__main__':
    unittest.main()