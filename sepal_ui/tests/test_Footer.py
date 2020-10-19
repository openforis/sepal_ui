import unittest
from datetime import datetime

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw

class TestFooter(unittest.TestCase):
    
    def test_init(self):
        
        #default init
        footer = sw.Footer()
        
        self.assertIsInstance(footer, v.Footer)
        self.assertEqual(footer.children[0], 'SEPAL \u00A9 {}'.format(datetime.today().year))
        
        #exhaustive 
        title = 'toto'
        footer = sw.Footer(title)
        self.assertEqual(footer.children[0], title)
        
        return
        
if __name__ == '__main__':
    unittest.main()