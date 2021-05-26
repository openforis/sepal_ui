import unittest
from traitlets import Any

from sepal_ui import model

class TestModel(unittest.TestCase):
    
    def test_export(self):
        
        # prepare the data 
        test_data = {'dummy1': 'test1', 'dummy2': 'test2'}
        
        # create a fake model class with 2 traits
        dummy = self.DummyClass()
        dummy.dummy1 = test_data['dummy1']
        dummy.dummy2 = test_data['dummy2']
        
        dict_ = dummy.export_data()
        
        # prepare the data 
        test_data = {'dummy1': 'test1', 'dummy2': 'test2'}
        
        # assert the result
        self.assertEqual(dict_, test_data)
        
        return
    
    def test_import(self):
        
        # prepare the data 
        test_data = {'dummy1': 'test1', 'dummy2': 'test2'}
        
        # create a fake model class with 2 traits
        dummy = self.DummyClass()
        
        dummy.import_data(test_data)
        
        # assert the result
        self.assertEqual(dummy.dummy1, test_data['dummy1'])
        self.assertEqual(dummy.dummy2, test_data['dummy2'])
        
        return 
        
    class DummyClass(model.Model):
        """
        Dummy class wit 2 traits
        """
        
        dummy1 = Any(None).tag(sync=True)
        dummy2 = Any(None).tag(sync=True)
        
if __name__ == '__main__':
    unittest.main()