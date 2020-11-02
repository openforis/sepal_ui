import unittest

from sepal_ui import sepalwidgets as sw

class TestFileInput(unittest.TestCase):
    
    def test_init(self):
        
        #default init
        fileinput = sw.FileInput()
        
        #####################################################
        ##      how to test the init list as the test      ##
        ##      is performed on git                        ##
        #####################################################

        self.assertIsInstance(fileinput, sw.FileInput)
        
        return
    
    def test_bind(self):
        
        fileinput = sw.FileInput()
        
        class Test_io:
            def __init__(self):
                self.out = None
                
        test_io = Test_io()
        
        output = sw.Alert()
        output.bind(fileinput, test_io, 'out')
        
        path = 'toto.ici.shp'
        fileinput.v_model = path
        
        self.assertEqual(test_io.out, path)
        self.assertTrue(output.viz)
        
        return        
        
if __name__ == '__main__':
    unittest.main()