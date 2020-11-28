import unittest
import random

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su

class TestUtils(unittest.TestCase):      
        
    def test_hide_component(self):
        
        # hide a normal v component 
        widget = v.Btn()
        su.hide_component(widget)
        self.assertIn('d-none', widget.class_)
        
        # hide a sepalwidget
        widget = sw.Btn()
        su.hide_component(widget)
        self.assertFalse(widget.viz)
        
        return 
    
    def test_show_component(self):
        
        # show a normal v component 
        widget = v.Btn()
        su.hide_component(widget)
        su.show_component(widget)
        self.assertNotIn('d-none', widget.class_)
        
        # show a sepalwidget
        widget = sw.Btn()
        su.hide_component(widget)
        su.show_component(widget)
        self.assertTrue(widget.viz)
        
        return 
    
    def test_get_gaul_dic(self):
        
        # search for France GAUL code 
        dict_ = su.get_gaul_dic()
        self.assertEqual(dict_['France'], 85)
        
        return 
    
    def get_iso_3(self):
        
        # search for France ISO-3 code
        self.assertEqual(su.get_iso_3('Fance'), 'FRA')
        
        return
    
    def test_download_link(self):
        
        # check the url for a 'toto/tutu.png' path
        
        return 
    
    def test_is_absolute(self):
        
        # test an absolute url (wikipedia home page)
        link = "https://fr.wikipedia.org/wiki/Wikipédia:Accueil_principal"
        self.assertTrue(su.is_absolute(link))
        
        # test a relative url ('toto/tutu.html')
        link = 'toto/tutu.html'
        self.assertFalse(su.is_absolute(link))
        
        return
    
    def test_random_string(self):
        
        # use a seed for the random function 
        random.seed(1)
        
        # check default length 
        str_ = su.random_string()
        self.assertEqual(len(str_), 3)
        self.assertEqual(str_, 'esz')
        
        # check parameter length 
        str_ = su.random_string(6)
        self.assertEqual(len(str_), 6)
        self.assertEqual(str_, 'ycidpy')
        
        return
    
    def test_get_file_size(self):
        
        # mock several file size and check the display 
        
        return 
    
    def test_init_ee(self):
        
        # check that no error is raised
        res = 1
        try:
            res = su.init_ee()
        except: 
            pass
        
        self.assertFalse(res)
        
        return
             
if __name__ == '__main__':
    unittest.main()