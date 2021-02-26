import unittest

from sepal_ui import sepalwidgets as sw

class TestPasswordField(unittest.TestCase):
    
    def test_init(self):
        
        # default init
        password = sw.PasswordField()
        
        self.assertIsInstance(password, sw.PasswordField)
        self.assertEqual(password.type, 'password')
        
        return
    
    def test_toogle_viz(self):
        
        # default init
        password = sw.PasswordField()
        
        # change the viz once 
        password._toggle_pwd(None, None, None)
        self.assertEqual(password.type, 'text')
        self.assertEqual(password.append_icon, 'mdi-eye')
        
        # change it a second time 
        password._toggle_pwd(None, None, None)
        self.assertEqual(password.type, 'password')
        self.assertEqual(password.append_icon, 'mdi-eye-off')
        
        return
        
if __name__ == '__main__':
    unittest.main()