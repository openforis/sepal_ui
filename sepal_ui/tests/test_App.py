import unittest

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw

class TestApp(unittest.TestCase):
    
    def test_init(self):
        
        #default init
        app = sw.App()
        self.assertIsInstance(app, sw.App)
        self.assertEqual(len(app.children), 3)
        self.assertIsInstance(app.children[0], sw.AppBar)
        self.assertIsInstance(app.children[1], v.Content)
        self.assertIsInstance(app.children[2], sw.Footer)
        
        #exhaustive 
        navDrawer = sw.NavDrawer([])
        appBar = sw.AppBar()
        tiles = []
        for i in range(5):
            tiles.append(sw.Tile('id_{}'.format(i), 'title_{}'.format(i)))
        footer = sw.Footer()
        
        app = sw.App(tiles, appBar, footer, navDrawer)
        self.assertIsInstance(app, sw.App)
        self.assertEqual(len(app.children), 4)
        self.assertIsInstance(app.children[0], sw.NavDrawer)
        self.assertIsInstance(app.children[1], sw.AppBar)
        self.assertIsInstance(app.children[2], v.Content)
        self.assertIsInstance(app.children[3], sw.Footer)
        
        return
    
    def test_show_tile(self):
        
        tiles = []
        for i in range(5):
            tiles.append(sw.Tile('id_{}'.format(i), 'title_{}'.format(i)))
            
        title = 'main_title'
        id_ = 'main_id' 
        main_tile = sw.Tile(id_, title)
        tiles.append(main_tile)
        
        app = sw.App(tiles)
        res = app.show_tile(id_)
        
        self.assertEqual(res, app)
        
        for tile in tiles:
            if tile == main_tile:
                self.assertTrue(tile.viz)
            else:
                self.assertFalse(tile.viz)
        
if __name__ == '__main__':
    unittest.main()