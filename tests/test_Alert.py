import unittest

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw

class TestAlert(unittest.TestCase):
    
    def test_init(self):
        alert = sw.Alert()
        self.assertFalse(alert.viz)
        self.assertEqual(alert.type, 'info')
        
        for type_ in sw.TYPES:
            alert = sw.Alert(type_)
            self.assertEqual(alert.type, type_)
            
        alert = sw.Alert('random')
        self.assertEqual(alert.type, 'info')
        
        return
        
    def test_add_msg(self):
        alert = sw.Alert()
        msg = 'toto'
        
        # single msg
        res = alert.add_msg(msg)
        self.assertEqual(res, alert)
        self.assertTrue(alert.viz)
        self.assertEqual(alert.children[0].children[0], msg)
        
        # single msg with type 
        for type_ in sw.TYPES:
            alert.add_msg(msg, type_)
            self.assertEqual(alert.type, type_)
            self.assertEqual(alert.children[0].children[0], msg)
            
        # single msg with rdm type
        alert.add_msg(msg, 'random')
        self.assertEqual(alert.type, 'info')
        self.assertEqual(alert.children[0].children[0], msg)
        
        return
        
    def test_add_live_msg(self):
        alert = sw.Alert()
        msg = 'toto'
        
        # single msg
        res = alert.add_live_msg(msg)
        self.assertEqual(res, alert)
        self.assertTrue(alert.viz)
        self.assertEqual(alert.children[1].children[0], msg)
        
        # single msg with type 
        for type_ in sw.TYPES:
            alert.add_live_msg(msg, type_)
            self.assertEqual(alert.type, type_)
            self.assertEqual(alert.children[1].children[0], msg)
            
        # single msg with rdm type
        alert.add_live_msg(msg, 'random')
        self.assertEqual(alert.type, 'info')
        self.assertEqual(alert.children[1].children[0], msg)
        
        return
    
    def test_append_msg(self):
        
        start = 'toto'
        msg = 'tutu'
        
        #test from empty alert 
        alert = sw.Alert()
        res = alert.append_msg(msg)
        
        self.assertEqual(res, alert)
        self.assertEqual(len(alert.children), 1)
        self.assertEqual(alert.children[0].children[0], msg)
        
        #test from non empty alert without divider 
        alert = sw.Alert().add_msg(start)
        res = alert.append_msg(msg)
        
        self.assertEqual(res, alert)
        self.assertEqual(len(alert.children), 2)
        self.assertEqual(alert.children[0].children[0], start)
        self.assertEqual(alert.children[1].children[0], msg)
        
        #test from non empty alert with divider
        alert = sw.Alert().add_msg(start)
        res = alert.append_msg(msg, True)
        
        self.assertEqual(res, alert)
        self.assertEqual(len(alert.children), 3)
        self.assertEqual(alert.children[0].children[0], start)
        self.assertIsInstance(alert.children[1], sw.Divider)
        self.assertEqual(alert.children[2].children[0], msg)
        
        # check that the divider is changing color 
        alert.type = 'success'
        self.assertIn(alert.children[1].type_, 'success')
        
        
    def test_bind(self):
        
        class Test_io: 
            
            def __init__(self):
                self.out = None
                
        test_io = Test_io()
        
        widget = v.TextField(v_model=None)
        alert = sw.Alert()
        alert2 = sw.Alert()
        alert3 = sw.Alert()
        alert4 = sw.Alert()
        
        # binding without text 
        res = alert.bind(widget, test_io, 'out')
        alert2.bind(widget, test_io, 'out', 'new variable : ')
        alert3.bind(widget, test_io, 'out', verbose=False)
        alert4.bind(widget, test_io, 'out', secret=True)
        
        self.assertEqual(res, alert)
        
        
        # check when value change
        msg = 'toto'
        widget.v_model = msg
        
        self.assertTrue(alert.viz)
        self.assertEqual(test_io.out, widget.v_model)
        
        self.assertEqual(alert.children[0].children[0], 'The selected variable is: {}'.format(msg))
        self.assertEqual(alert2.children[0].children[0], 'new variable : {}'.format(msg))
        self.assertFalse(len(alert3.children))
        self.assertEqual(alert4.children[0].children[0], 'The selected variable is: {}'.format("*" * len(msg)))
        
        return 
    
    def test_check_input(self): 
        
        alert = sw.Alert()

        var_test = None
        res = alert.check_input(var_test)
        self.assertFalse(res)
        self.assertTrue(alert.viz)
        self.assertEqual(alert.children[0].children[0], 'The value has not been initialized')
        
        res = alert.check_input(var_test, 'toto')
        self.assertEqual(alert.children[0].children[0], 'toto')
        
        var_test = 1 
        res = alert.check_input(var_test)
        self.assertTrue(res)
        
        # test lists 
        var_test = [range(2)]
        res = alert.check_input(var_test)
        self.assertTrue(res)
        
        # test empty list 
        var_test = []
        res = alert.check_input(var_test)
        self.assertFalse(res)
        
        return 
    
    def test_reset(self):
        
        alert = sw.Alert().add_msg('toto').reset()
        
        self.assertFalse(alert.viz)
        self.assertEqual(len(alert.children), 1)
        self.assertEqual(alert.children[0], '')
        
        return
        
    def test_rmv_last_msg(self):
        
        # check with a no msg alert 
        alert = sw.Alert().remove_last_msg()
        
        self.assertFalse(alert.viz)
        self.assertEqual(alert.children[0], '')
        
        # check with a 1 msg alert
        alert = sw.Alert().add_msg('toto').remove_last_msg()
        
        self.assertFalse(alert.viz)
        self.assertEqual(alert.children[0], '')
        
        # check with a multiple msg alert 
        alert = sw.Alert()
        
        string = 'toto'
        nb_msg = 5
        for i in range(nb_msg):
            alert.append_msg(f'{string}{i}')
            
        alert.remove_last_msg()
        
        self.assertTrue(alert.viz)
        self.assertEqual(len(alert.children), 4)
        self.assertEqual(alert.children[nb_msg-2].children[0], f'{string}{nb_msg-2}')
        
        return
    
    def test_update_progress(self):
        
        # create an alert 
        alert = sw.Alert()
        
        # test a random update 
        alert.update_progress(0.5)
        self.assertEqual(alert.children[1].children[0].children[2].children[0], ' 50.0%')
        
if __name__ == '__main__':
    unittest.main()