import unittest

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw

class TestNavDrawer(unittest.TestCase):
    
    def test_init(self):
        
        items = []
        for i in range(5):
            items.append(sw.DrawerItem('title {}'.format(i)))
        
        #default init
        widget = sw.NavDrawer(items)
        self.assertIsInstance(widget, sw.NavDrawer)
        self.assertEqual(widget.children[0].children, items)
        
        #exhaustive
        code = "#code"
        wiki = "#wiki"
        issue = "#issue"
        
        #test all composition of links
        widget = sw.NavDrawer(items, code)
        self.assertEqual(len(widget.children[2].children), 1)
        self.assertEqual(widget.children[2].children[0].href, code)
        
        widget = sw.NavDrawer(items, None, wiki)
        self.assertEqual(len(widget.children[2].children), 1)
        self.assertEqual(widget.children[2].children[0].href, wiki)
        
        widget = sw.NavDrawer(items, None, None, issue)
        self.assertEqual(len(widget.children[2].children), 1)
        self.assertEqual(widget.children[2].children[0].href, issue)
        
        widget = sw.NavDrawer(items, code, wiki)
        self.assertEqual(len(widget.children[2].children), 2)
        self.assertEqual(widget.children[2].children[0].href, code)
        self.assertEqual(widget.children[2].children[1].href, wiki)
        
        widget = sw.NavDrawer(items, None, wiki, issue)
        self.assertEqual(len(widget.children[2].children), 2)
        self.assertEqual(widget.children[2].children[0].href, wiki)
        self.assertEqual(widget.children[2].children[1].href, issue)
        
        widget = sw.NavDrawer(items, code, None, issue)
        self.assertEqual(len(widget.children[2].children), 2)
        self.assertEqual(widget.children[2].children[0].href, code)
        self.assertEqual(widget.children[2].children[1].href, issue)
        
        widget = sw.NavDrawer(items, code, wiki, issue)
        self.assertEqual(len(widget.children[2].children), 3)
        self.assertEqual(widget.children[2].children[0].href, code)
        self.assertEqual(widget.children[2].children[1].href, wiki)
        self.assertEqual(widget.children[2].children[2].href, issue)
        
        return
    
    def test_display_drawer(self):
        
        ##############################################
        ##      how to test the on click event      ##
        ##############################################
        
        self.assertEqual(True, True)
        
        return
        
if __name__ == '__main__':
    unittest.main()