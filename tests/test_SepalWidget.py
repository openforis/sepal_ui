import unittest

from sepal_ui import sepalwidgets as sw

class TestSepalWidget(unittest.TestCase):
    
    def test_init(self):
        widget = sw.SepalWidget()
        self.assertTrue(widget.viz, 'widget not visible')
        
        return
        
    def test_show(self):
        widget = sw.SepalWidget()
        widget.class_ = 'd-none'
        widget.show()
        self.assertTrue(widget.viz, 'widget not visible')
        self.assertNotIn('d-none', str(widget.class_).strip(), 'widget has d-none class')
        
        return
        
    def test_hide(self):
        widget = sw.SepalWidget()
        widget.class_ = None
        widget.hide()
        self.assertFalse(widget.viz, 'widget remain visible')
        self.assertIn('d-none', str(widget.class_).strip(), "widget hasn't d-none class")
        
        return
        
    def test_toggle_viz(self):
        widget = sw.SepalWidget()
        widget.class_ = None
        self.assertTrue(widget.viz, 'widget not visible')
        self.assertNotIn('d-none', str(widget.class_).strip(), 'widget has d-none class')
        
        widget.toggle_viz()
        self.assertFalse(widget.viz, 'widget remain visible')
        self.assertIn('d-none', str(widget.class_).strip(), "widget hasn't d-none class")
        
        widget.toggle_viz()
        self.assertTrue(widget.viz, 'widget not visible')
        self.assertNotIn('d-none', str(widget.class_).strip(), 'widget has d-none class')
        
        return
        
    def test_reset(self):
        
        widget = sw.SepalWidget()
        widget.v_model = 'toto'
        
        widget.reset()
        
        self.assertEqual(widget.v_model, None)
        
        return

if __name__ == '__main__':
    unittest.main()