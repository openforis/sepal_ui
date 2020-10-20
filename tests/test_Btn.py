import unittest

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw

class TestBtn(unittest.TestCase):      
        
    def test_init(self):
        
        #minimal btn
        btn = sw.Btn()
        self.assertEqual(btn.color, 'primary')
        self.assertEqual(btn.v_icon, None)
        self.assertEqual(btn.children[0], 'Click')
        
        #extensive btn
        btn = sw.Btn('toto', 'mdi-folder')
        self.assertEqual(btn.children[1], 'toto')
        self.assertIsInstance(btn.v_icon, v.Icon)
        self.assertEqual(btn.v_icon.children[0], 'mdi-folder')
        
        return 
    
    def test_set_icon(self):
        
        btn = sw.Btn()
        res = btn.set_icon('mdi-folder')
        self.assertIsInstance(btn.v_icon, v.Icon)
        self.assertEqual(btn.v_icon.children[0], 'mdi-folder')
        self.assertEqual(res, btn)
        
        return 
    
    def test_toggle_loading(self):
        
        btn = sw.Btn()
        res = btn.toggle_loading()
        
        self.assertTrue(btn.loading)
        self.assertTrue(btn.disabled)
        self.assertEqual(res, btn)
        
        btn.toggle_loading()
        self.assertFalse(btn.loading)
        self.assertFalse(btn.disabled)
        
        return
        
if __name__ == '__main__':
    unittest.main()