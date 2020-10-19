import unittest
from datetime import datetime

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw

class TestDrawerItem(unittest.TestCase):
    
    def test_init_cards(self):
        title = 'toto'
        id_ = 'toto_id'
        icon = 'mdi-folder'
        
        #default init
        drawerItem = sw.DrawerItem(title)
        self.assertIsInstance(drawerItem, v.ListItem)
        self.assertIsInstance(drawerItem.children[0].children[0], v.Icon)
        self.assertEqual(drawerItem.children[0].children[0].children[0], 'mdi-folder-outline')
        self.assertIsInstance(drawerItem.children[1].children[0], v.ListItemTitle)
        self.assertEqual(drawerItem.children[1].children[0].children[0], title)
        
        #exhaustive 
        drawerItem = sw.DrawerItem(title, icon, id_)
        self.assertEqual(drawerItem.children[0].children[0].children[0], icon)
        self.assertEqual(drawerItem.children[1].children[0].children[0], title)
        self.assertEqual(drawerItem._metadata['card_id'], id_)
        
        
        #too much args 
        drawerItem = sw.DrawerItem(title, icon, id_, '#')
        self.assertEqual(drawerItem.href, '#')
        self.assertEqual(drawerItem.target, '_blank')
        self.assertEqual(drawerItem._metadata, None)
        
        return
    
    def test_display_tile(self):
        
        tiles = []
        for i in range(5):
            title = 'name_{}'.format(i)
            id_ = 'id_{}'.format(i)
            tiles.append(sw.Tile(id_, title))
            
        title = 'toto'
        id_ = 'toto_id'
        
        real_tile = sw.Tile(id_, title)
        tiles.append(real_tile)
        
        drawerItem = sw.DrawerItem(title, None, id_)
        
        res = drawerItem.display_tile(tiles)
        self.assertEqual(res, drawerItem)
        
        ##############################################################
        ##      TODO cannot test the javascript on_click event      ##
        ##############################################################
        return
        
if __name__ == '__main__':
    unittest.main()