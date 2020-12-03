import unittest
import random
from unittest.mock import patch

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
        iso_code = su.get_iso_3('Fance') 
        self.assertEqual(iso_code, 'FRA')
        
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
        
        # init test values
        test_value = 7.5
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        
        # mock 0 B file 
        with patch('os.path.getsize', return_value=0):
            txt = su.get_file_size('random')
            self.assertEqual(txt, '0B')
        
        # mock every pow of 1024 to YB
        for i in range(9):
            with patch('os.path.getsize', return_value=test_value*(1024**i)):
                txt = su.get_file_size('random')
                self.assertEqual(txt, f'7.5 {size_name[i]}')
        
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