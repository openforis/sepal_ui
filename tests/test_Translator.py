import unittest
from pathlib import Path
from sepal_ui.translator import Translator

class TestTranslator(unittest.TestCase):      
        
    def test_init(self):
        
        # assert that the test key exist in fr 
        target_lan = 'fr'
        translator = Translator(self._get_message_json_folder(), target_lan)
        
        self.assertEqual(translator.test_key, 'Clef test')
        
        # assert that the test does not exist in es and we fallback to en 
        target_lan = 'es'
        translator = Translator(self._get_message_json_folder(), target_lan)
        
        self.assertEqual(translator.test_key, 'Test key')
        
        return
    
    def test_missing_keys(self):
        
        # assert that all the keys exist in fr 
        target_lan = 'fr'
        translator = Translator(self._get_message_json_folder(), target_lan)
        
        self.assertEqual(translator.missing_keys(), 'All messages are translated')
        
        # assert that the test does not exist in es and we fallback to en 
        target_lan = 'es'
        translator = Translator(self._get_message_json_folder(), target_lan)
        
        self.assertIn("root['test_key']", translator.missing_keys())
        
        return 
    
    def _get_message_json_folder(self):
        
        # use the json folder of the lib 
        home = Path(__file__).parent.parent.absolute()
        path = home.joinpath('sepal_ui', 'message')
        
        return path
        
if __name__ == '__main__':
    unittest.main()