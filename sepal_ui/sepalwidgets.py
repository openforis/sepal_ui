#!/usr/bin/env python3
from markdown import markdown
from datetime import datetime
import traitlets
import os

import ipyvuetify as v

from sepal_ui.scripts import utils

class SepalWidget(v.VuetifyWidget):
    
    MAIN_COLOR = '#2e7d32'
    DARKER_COLOR = '#005005'
    
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
    
    def hide(self):
        """add the d-none html class to the widget"""
        if not 'd-none' in self.class_:
            self.class_ = self.class_.strip() + ' d-none'
        
    def show(self):
        """ remove the d-none html class to the widget"""
        if 'd-none' in self.class_:
            self.class_ = self.class_.replace('d-none', '')

class Alert(v.Alert, SepalWidget):
    """create an alert widget that can be used to display the process outputs"""
    
    TYPES = ('info', 'error', 'warning', 'success')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.children = ['']
        self.type = 'info'
        self.text = True
        self.clear()
    
    def add_msg(self, msg, type_='info'):
        self.show()
        self.type = type_ if (type_ in self.TYPES) else self.TYPES[0]
        self.children = [msg]
        
    def clear(self):
        self.hide()
        self.children = ['']


class Btn(v.Btn, SepalWidget):
    """
    Creates a process button filled with the provided text
    
    Returns: 
        btn (v.Btn) :
    """
    

    def __init__(self, text='Click', icon =None, **kwargs):
        super().__init__(**kwargs)
        self.color='primary'
        
        if icon:
            self.children=[self.set_icon(icon), text]
        else:
            self.children=[text]

    def set_icon(self, icon):

        common_icons = {
            'default' : 'mdi-adjust',
            'download' : 'mdi-download'
        }
        
        if not icon in common_icons.keys():
            icon = 'default'
        
        return v.Icon(left=True, children=[common_icons[icon]])    
        
    def toggle_loading(self):
        """disable and start loading or reverse"""
        self.loading = not self.loading
        self.disabled = self.loading

class AppBar (v.AppBar, SepalWidget):
    """create an appBar widget with the provided title using the sepal color framework"""
    def __init__(self, title='SEPAL module', **kwargs):
        
        super().__init__(**kwargs)
        
        self.title = title
        self.toolBarButton = v.Btn(
            icon = True, 
            children=[
                v.Icon(class_="white--text", children=['mdi-dots-vertical'])
            ]
        )
        
        self.color=self.MAIN_COLOR,
        self.class_="white--text",
        self.dense=True,
        self.app = True,
        self.children = [
            self.toolBarButton, 
            v.ToolbarTitle(children=[title])
        ]
        
        def setTitle(self, title):
            """set the title in the appbar"""
            self.title = title
            
            self.children = [
                self.toolBarButton, 
                v.ToolbarTitle(children=[title])
            ]
            
class DrawerItem(v.ListItem, SepalWidget):
    """create a drawer item using the user input"""
    
    def __init__(self, title, icon=None, card='', href='', **kwargs):
        
        super().__init__(**kwargs)
        
        icon = icon if icon else 'mdi-folder-outline'
        
        self.link=True
        self.children = [
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
        
        if not href == '':
            self.href=href
            self.target="_blank"
        
        if not card == '':
            self._metadata = {'card_id': card }
            
class NavDrawer(v.NavigationDrawer, SepalWidget):
        """ 
    create a navdrawer using the different items of the user and the sepal color framework. The drawer can include links to the github page of the project for wiki, bugs and repository.
    """
        
        def __init__(self, items, code=None, wiki=None, issue=None, **kwargs):
            
            super().__init__(**kwargs)
            
            
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
                
            self.v_model=True
            self.app=True,
            self.color = self.DARKER_COLOR
            self.children = [
                v.List(dense=True, children=items),
                v.Divider(),
                v.List(dense=True, children=code_link)
            ]
            
class Footer(v.Footer, SepalWidget):
    """create a footer with cuzomizable text. Not yet capable of displaying logos"""
    def __init__(text="", **kwargs):
        
        super().__init__(text ='', **kwargs)
        
        text = text if text != '' else 'SEPAL \u00A9 2020'
        
        self.color = self.MAIN_COLOR
        self.class_ = "white--text"
        self.app=True
        self.children = [text]
        
class App (v.App, SepalWidget):
        """Create an app display with the tiles created by the user. Display false footer and appBar if not filled. navdrawer is fully optionnal
        """
        
        def __init__(tiles=[''], appBar=None, footer=None, navDrawer=None, **kwargs):
            
            super().__init__(**kwarg)
            
            self.v_model=None
            
            #add the navDrawer if existing
            if navDrawer:
                app_children.append(navDrawer)
    
            #create a false appBar if necessary
            if not appBar:
                appBar = AppBar()
            app_children.append(appBar)

            #add the content of the app
            content = v.Content(children=[
                v.Container(fluid=True,children = tiles)
            ])
            app_children.append(content)
    
            #create a false footer if necessary
            if not footer:
                footer = Footer()
            app_children.append(footer)

            self.children = app_children
            
class Tile(v.Layout, SepalWidget):
    """create a customizable tile for the sepal UI framework"""
    
    def __init__(self, id_, title, inputs=[''], btn=None, output=None, **kwargs):
        
        if btn:
            inputs.append(btn)
        
        if output:
            inputs.append(output)
            
        children = [v.Html(xs12=True, tag='h2', children=[title])]
        children += [v.Flex(xs12=True, children=[widget]) for widget in inputs]
        
        card = v.Card(
            class_="pa-5",
            raised=True,
            xs12=True,
            children=children
        )
        
        super().__init__(
            _metadata={'mount_id': id_},
            row=True,
            align_center=True,
            class_="ma-5 d-inline",
            xs12=True,
            children = [card],
            **kwargs
        )
        
class TileAbout(Tile):
    """
    create a about tile using a md file. This tile will have the "about_widget" id and "About" title."""
    
    def __init__(self, pathname, **kwargs):
        
        #read the content and transform it into a html
        f = open(pathname, 'r')
        if f.mode == 'r':
            about = f.read()
        else :
            about = '**No About File**'
        
        about = markdown(about, extensions=['fenced_code','sane_lists'])
    
        #need to be nested in a div to be displayed
        about = '<div>\n' + about + '\n</div>'
    
        #create a Html widget
        class MyHTML(v.VuetifyTemplate):
            template = traitlets.Unicode(about).tag(sync=True)
    
    
        content = MyHTML()
        
        super().__init__('about_widget', 'About', inputs=[content], **kwargs)
        
class TileDisclaimer(Tile):
    """
    create a about tile using a md file. This tile will have the "about_widget" id and "About" title."""
    
    def __init__(**kwargs):
        
        pathname = os.path.join(os.path.dirname(__file__), 'scripts', 'disclaimer.md')
        
        #read the content and transform it into a html
        f = open(pathname, 'r')
        if f.mode == 'r':
            about = f.read()
        else :
            about = '**No Disclaimer File**'
        
        about = markdown(about, extensions=['fenced_code','sane_lists'])
    
        #need to be nested in a div to be displayed
        about = '<div>\n' + about + '\n</div>'
    
        #create a Html widget
        class MyHTML(v.VuetifyTemplate):
            template = traitlets.Unicode(about).tag(sync=True)
    
    
        content = MyHTML()
        
        super().__init__('about_widget', 'Disclaimer', inputs=[content], **kwargs)

        
class DownloadBtn(v.Btn, SepalWidget):
    """Create a green downloading button with the user text"""
    
    def __init__(text, path='#', **kwargs):
        
        super().__init__(**kwargs)
        
        #create the url
        if utils.is_absolute(path):
            url = path
        else: 
            url = utils.create_download_link(path)
    
        self.class_='ma-2',
        self.xs5=True,
        self.color='success',
        self.href=url,
        self.children=[
            v.Icon(left=True, children=['mdi-download']),
            text
        ]
        

        