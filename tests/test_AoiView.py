import unittest

import ee

from sepal_ui import aoi
from sepal_ui.mapping import SepalMap
from sepal_ui.message import ms

class TestAoiTile(unittest.TestCase):
    
    FOLDER = 'projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test'

    def test_init(self):
        
        # default init
        view = aoi.AoiView(folder = self.FOLDER)
        self.assertIsInstance(view, aoi.AoiView)    
        
        # init with ee 
        view = aoi.AoiView(folder= self.FOLDER, gee=False)
        self.assertFalse(view.model.ee)
        
        # init with a map 
        m = SepalMap(dc=True)
        view = aoi.AoiView(map_=m)
        self.assertEqual(view.map_, m)
        
        return
    
    def test_admin(self):
        
        # test if admin0 is in Gaul
        view = aoi.AoiView(folder = self.FOLDER)
        first_gaul_item = {'text': 'Abyei', 'value': 102}
        self.assertEqual(first_gaul_item, view.w_admin_0.items[0])
        
        # test if admin0 is in gadm
        view = aoi.AoiView(gee=False, folder = self.FOLDER)
        first_gadm_item = {'text': 'Afghanistan', 'value': 'AFG'}
        self.assertEqual(first_gadm_item, view.w_admin_0.items[0])
        
        return
        
    def test_activate(self):
        
        # test the activation of the widgets 
        view = aoi.AoiView(folder=self.FOLDER)
        
        for method in aoi.AoiModel.METHODS:
            
            view.w_method.v_model = method
            
            for k, c in view.components.items():
                
                if k == method:
                    self.assertNotIn('d-none', c.class_)
                elif hasattr(c, 'parent'):
                    if view.components[k].parent == c: #or view.components[k].parent.parent == c:
                        self.assertNotIn('d-none', c.class_)
                else:
                    self.assertIn('d-none', c.class_)
                    
        return
        
if __name__ == '__main__':
    unittest.main()