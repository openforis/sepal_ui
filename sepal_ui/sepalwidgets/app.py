from functools import partial
from datetime import datetime

import ipyvuetify as v
import traitlets

from sepal_ui.sepalwidgets.sepalwidget import SepalWidget
from sepal_ui.frontend.styles import *
from sepal_ui.frontend.js import *

class AppBar (v.AppBar, SepalWidget):
    """create an appBar widget with the provided title using the sepal color framework"""
    
    def __init__(self, title='SEPAL module', **kwargs):
        
        self.toggle_button = v.Btn(
            icon = True, 
            children=[
                v.Icon(class_="white--text", children=['mdi-dots-vertical'])
            ]
        )
        
        super().__init__(
            color=sepal_main,
            class_="white--text",
            dense=True,
            app = True,
            children = [self.toggle_button, v.ToolbarTitle(children=[title])],
            **kwargs
        )
        
    def set_title(self, title):
        """set the title in the appbar"""
            
        self.children = [
            self.toggle_button, 
            v.ToolbarTitle(children=[title])
        ]
            
        return self
            
class DrawerItem(v.ListItem, SepalWidget):
    """create a drawer item using the user input"""
    
    def __init__(self, title, icon=None, card=None, href=None, **kwargs):
        
        icon = icon if icon else 'mdi-folder-outline'
        
        children = [
            v.ListItemAction(
                children=[
                    v.Icon(
                        class_="white--text", 
                        children=[icon])
                ]
            ),
            v.ListItemContent(
                children=[
                    v.ListItemTitle(
                        class_="white--text", 
                        children=[title]
                    )
                ]
            )
        ]
        
        super().__init__(
            link=True,
            children=children,
            **kwargs) 

        
        if href:
            self.href=href
            self.target="_blank"
        elif card:
            self._metadata = {'card_id': card }
            
        self.rt = ResizeTrigger()
            
    def display_tile(self, tiles):
        """
        display the apropriate tiles when the item is clicked
    
        Args:
            tiles ([v.Layout]) : the list of all the available tiles in the app
        """            
    
        self.on_event('click', partial(self._on_click, tiles=tiles))
        
        return self
    
    def _on_click(self, widget, event, data, tiles):
        
        for tile in tiles:
            if self._metadata['card_id'] == tile._metadata['mount_id']:
                tile.show()
            else:
                tile.hide()
                    
        # trigger the risize event 
        rt.resize += 1
        
        return self
            
class NavDrawer(v.NavigationDrawer, SepalWidget):
        """ 
    create a navdrawer using the different items of the user and the sepal color framework. The drawer can include links to the github page of the project for wiki, bugs and repository.
    """
        
        def __init__(self, items=[], code=None, wiki=None, issue=None, **kwargs):
            
            code_link = []
            if code:
                item_code = DrawerItem('Source code', icon='mdi-file-code', href=code)
                code_link.append(item_code)
            if wiki:
                item_wiki = DrawerItem('Wiki', icon='mdi-book-open-page-variant', href=wiki)
                code_link.append(item_wiki)
            if issue:
                item_bug = DrawerItem('Bug report', icon='mdi-bug', href=issue)
                code_link.append(item_bug)
                
            super().__init__(
                v_model=True,
                app=True,
                color = sepal_darker,
                children = [
                    v.List(dense=True, children=items),
                    v.Divider(),
                    v.List(dense=True, children=code_link)
                ],
                **kwargs
            )
            
        def display_drawer(self, toggleButton):
            """
            bind the drawer to it's toggleButton

            Args:
                drawer (v.navigationDrawer) : the drawer tobe displayed
                toggleButton(v.Btn) : the button that activate the drawer
            """
            toggleButton.on_event('click', self._on_drawer_click)
                
            return self
        
        def _on_drawer_click(self, widget, event, data):
            self.v_model = not self.v_model

class Footer(v.Footer, SepalWidget):
    """create a footer with cuzomizable text. Not yet capable of displaying logos"""
    def __init__(self, text="", **kwargs):
        
        text = text if text != '' else 'SEPAL \u00A9 {}'.format(datetime.today().year)
        
        super().__init__(
            color = sepal_main,
            class_ = "white--text",
            app=True,
            children = [text],
            **kwargs
        )
        
class App(v.App, SepalWidget):
        """Create an app display with the tiles created by the user. Display false footer and appBar if not filled. navdrawer is fully optionnal
        """
        
        def __init__(self, tiles=[''], appBar=None, footer=None, navDrawer=None, **kwargs):
            
            self.tiles = None if tiles == [''] else tiles
            
            app_children = []
            
            # add the navDrawer if existing
            if navDrawer:
                self.navDrawer = navDrawer
                app_children.append(self.navDrawer)
    
            # create a false appBar if necessary
            if not appBar:
                appBar = AppBar()
            self.appBar = appBar
            app_children.append(self.appBar)

            # add the content of the app
            self.content = v.Content(children=[
                v.Container(fluid=True,children = tiles)
            ])
            app_children.append(self.content)
    
            # add the footer if existing
            if footer:
                self.footer = footer
                app_children.append(self.footer)
            
            super().__init__(
                v_model=None,
                children = app_children,
                **kwargs)
            
        def show_tile(self, name):
            """select the tile to display using its mount-id"""
            for tile in self.tiles:
                if name == tile._metadata['mount_id']:
                    tile.show()
                else:
                    tile.hide()
            
            return self