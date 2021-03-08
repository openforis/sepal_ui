from functools import partial
from datetime import datetime

import ipyvuetify as v
import traitlets

from sepal_ui.sepalwidgets.sepalwidget import SepalWidget
from sepal_ui.frontend.styles import *
from sepal_ui.frontend.js import *

class AppBar (v.AppBar, SepalWidget):
    """
    Custom AppBar widget with the provided title using the sepal color framework
    
    Args: 
        title (str, optional): the title of the app
        
    Attributes:
        toggle_button (v.Btn): the btn to display or hide the drawer to the user
        title (v.ToolBarTitle): the widget containing the app title
    """
    
    def __init__(self, title='SEPAL module', **kwargs):
        
        self.toggle_button = v.Btn(
            icon = True, 
            children=[
                v.Icon(class_="white--text", children=['mdi-dots-vertical'])
            ]
        )
        
        self.title = v.ToolbarTitle(children=[title])
        
        super().__init__(
            color=sepal_main,
            class_="white--text",
            dense=True,
            app = True,
            children = [self.toggle_button, self.title],
            **kwargs
        )
        
    def set_title(self, title):
        """
        Set the title of the appBar
        
        Args:
            title (str): the new app title
            
        Return:
            self
        """
        
        self.title.children = [title]
            
        return self
            
class DrawerItem(v.ListItem, SepalWidget):
    """
    Custom DrawerItem using the user input. 
    If a card is set the drawerItem will trigger the display of all the Tiles in the app that have the same mount_id.
    If an href is set, the drawer will open the link in a new tab
    
    Args:
        title (str): the title of the drawer item
        icon(str, optional): the full name of a mdi-icon
        card (str, optional): the mount_id of tiles in the app
        href (str, optional): the absolute link to an external webpage
        
    Attributes:
        href (str): the absolute link to follow on click 
        _metadata (dict): single key dict to point to a mount_id. This ount_id will be used as parameter to know which tiles are to be shown on click event
        rt (ResizeTrigger): the trigger to resize maps and other javascript object when jumping from a tile to another
    """
    
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
        
                        
    def display_tile(self, tiles):
        """
        Display the apropriate tiles when the item is clicked.
        The tile to display will be all tile in the list with the mount_id as the current object
    
        Args:
            tiles ([sw.Tile]) : the list of all the available tiles in the app
            
        Return:
            self
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
                
        # change the cuurent item status 
        self.input_value = True
        
        return self
            
class NavDrawer(v.NavigationDrawer, SepalWidget):
    """ 
    Custom NavDrawer using the different DrawerItems of the user and the sepal color framework. 
    The drawer can include links to the github page of the project for wiki, bugs and repository.
    
    Args:
        item ([sw.DrawerItem]): the list of all the drawerItem to display in the drawer. This items should pilote the different tile visibility
        code (str, optional): the absolute link to the source code 
        wiki (str, optional): the absolute link the the wiki page
        issue (str, optional): the absolute link to the issue tracker
    """
        
    def __init__(self, items=[], code=None, wiki=None, issue=None, **kwargs):
        
        self.items = items
        
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
                v.List(dense=True, children=self.items),
                v.Divider(),
                v.List(dense=True, children=code_link)
            ],
            **kwargs
        )
        
        # bind the javascripts behaviour
        for i in self.items:
            i.observe(self._on_item_click, 'input_value')
        
    def display_drawer(self, toggleButton):
        """
        Bind the drawer to the app toggleButton

        Args:
            toggleButton(v.Btn) : the button that activate the drawer
        """
        
        toggleButton.on_event('click', self._on_drawer_click)
            
        return self
    
    def _on_drawer_click(self, widget, event, data):
        """
        Toggle the drawer visibility
        """
        
        self.v_model = not self.v_model
        
        return self
        
    def _on_item_click(self, change):
        """
        Deactivate all the other items when on of the is activated
        """
        if change['new'] == False:
            return self
        
        # reset all others states
        for i in self.items:
            if i != change['owner']:
                i.input_value = False
            
        return self
        

class Footer(v.Footer, SepalWidget):
    """
    Custom Footer with cuzomizable text. 
    Not yet capable of displaying logos
    
    Args: 
        text (str, optional): the text to display in the future
    """
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
        """
        Custom App display with the tiles created by the user using the sepal color framework.
        Display false appBar if not filled. Navdrawer is fully optionnal.
        The drawerItem will be linked to the app tile and they will be able to control their display
        If the navdrawer exist, it will be linked to the appbar togglebtn
        
        Args:
            tiles ([sw.Tile]): the tiles of the app
            appBar (sw.AppBar, optional): the appBar of the application
            footer (sw.Footer, optional): the footer of the application
            navDrawer (sw.NavDrawer): the navdrawer of the application
            
        Attributes:
            tiles ([sw.Tile]): the tiles of the app
            appBar (sw.AppBar, optional): the appBar of the application
            footer (sw.Footer, optional): the footer of the application
            navDrawer (sw.NavDrawer): the navdrawer of the application
            content (v.Content): the tiles organized in a fluid container
            
        """
        
        def __init__(self, tiles=[''], appBar=None, footer=None, navDrawer=None, **kwargs):
            
            self.tiles = None if tiles == [''] else tiles
            
            app_children = []
            
            # create a false appBar if necessary
            if not appBar:
                appBar = AppBar()
            self.appBar = appBar
            app_children.append(self.appBar)
            
            # add the navDrawer if existing
            self.navDrawer = None
            if navDrawer:
                # bind app tile list to the navdrawer
                for di in navDrawer.items:
                    di.display_tile(tiles)
                    
                # link it with the appbar
                navDrawer.display_drawer(self.appBar.toggle_button)
                
                # add the drawers to the children
                self.navDrawer = navDrawer
                app_children.append(self.navDrawer)

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
            """
            Select the tile to display when the app is launched
            
            Args:
                name (str): the mount-id of the tile(s) to display
            
            Return:
                self
            """
            # show the tile 
            for tile in self.tiles:
                if name == tile._metadata['mount_id']:
                    tile.show()
                else:
                    tile.hide()
            
            # activate the drawerItem
            if self.navDrawer:
                for i in self.navDrawer.items:
                    if name == i._metadata['card_id']:
                        i.input_value = True
                        
            return self