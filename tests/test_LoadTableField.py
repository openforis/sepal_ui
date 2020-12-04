import unittest
import os

import pandas as pd

from sepal_ui import sepalwidgets as sw

class TestLoadTableField(unittest.TestCase):
    
    def test_init(self):
        
        # init variables 
        load_table = sw.LoadTableField()
        
        self.assertIsInstance(load_table, sw.LoadTableField)
        
        return 
    
    def test_on_file_input_change(self):
        
        # init var 
        test_file = self._create_fake_table()
        load_table = sw.LoadTableField()
        
        # change the value of the file 
        load_table._on_file_input_change({'new': test_file})
        
        test_data = {
            'pathname': test_file,
            'id_column': 'id',
            'lng_column': 'lng',
            'lat_column': 'lat'
        }
        
        self.assertEqual(load_table.get_v_model(), test_data)
        self.assertEqual(load_table.get_pathname(), test_data['pathname'])
        self.assertEqual(load_table.get_id_lbl(), test_data['id_column'])
        self.assertEqual(load_table.get_lng_lbl(), test_data['lng_column'])
        self.assertEqual(load_table.get_lat_lbl(), test_data['lat_column'])
        
        # delete the test file 
        os.remove(test_file)
        
        return
    
    def _create_fake_table(self):
        
        root_dir = os.path.expanduser('~')
        filename = f'{root_dir}/test.csv'
        
        coloseo = [1, 41.89042582290999, 12.492241627092199]
        fao = [2, 41.88369224629387, 12.489216069409004]
        df = pd.DataFrame([coloseo, fao], columns=['id', 'lat', 'lng'])
        
        df.to_csv(filename, index = False)
        
        return filename       
        
if __name__ == '__main__':
    unittest.main()