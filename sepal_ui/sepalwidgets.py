#!/usr/bin/env python3
from functools import partial
from markdown import markdown
from datetime import datetime
import traitlets
import os

import ipyvuetify as v

from sepal_ui.scripts import utils
from sepal_ui.scripts import messages as ms

############################
##   hard coded colors    ##
############################

sepal_main = '#2e7d32'
sepal_darker = '#005005'

###########################
##       classes         ##
###########################
class SepalWidget(v.VuetifyWidget):
    
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        self.viz = True
        
    def toggle_viz(self):
        """toogle the visibility of the widget"""
        if self.viz:
            self.hide()
        else:
            self.show()
        
        return self
    
    def hide(self):
        """add the d-none html class to the widget"""
        if not 'd-none' in str(self.class_):
            self.class_ = str(self.class_).strip() + ' d-none'
        self.viz = False
        
        return self
        
    def show(self):
        """ remove the d-none html class to the widget"""
        if 'd-none' in str(self.class_):
            self.class_ = str(self.class_).replace('d-none', '')
        self.viz = True
        
        return self

class Alert(v.Alert, SepalWidget):
    """create an alert widget that can be used to display the process outputs"""
    
    TYPES = ('secondary', 'primary', 'info', 'error', 'warning', 'success')
    
    def __init__(self, type_='info', **kwargs):
        
        type_ = type_ if (type_ in self.TYPES) else self.TYPES[0]
        
        super().__init__(
            children = [''],
            type = type_,
            text = True,
            class_="mt-5",
            **kwargs
        )
        
        self.hide()
        
    
    def add_msg(self, msg, type_='info'):
        self.show()
        self.type = type_ if (type_ in self.TYPES) else self.TYPES[0]
        self.children = [msg]
        
        return self
    
    def add_live_msg(self, msg, type_='info'):
        
        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        self.show()
        self.type = type_ if (type_ in self.TYPES) else self.TYPES[0]
    
        self.children = [
            v.Html(tag='p', children=['[{}]'.format(current_time)]),
            v.Html(tag='p', children=[msg])
       ]
        
        return self
        
    def reset(self):
        self.children = ['']
        self.hide()
        
        return self 
    
    def bind(self, widget, obj, variable, msg=None):
        """ 
        bind the variable to the widget and display it in the alert
    
        Args:
            widget (v.XX) : an ipyvuetify input element
            obj : the process_io object
            variable (str) : the name of the member in process_io object
            output_message (str, optionnal) : the output message before the variable display
        """
        if not msg: msg = 'The selected variable is: '
            
        def on_change(widget, event, data, obj, variable, output, msg):
        
            setattr(obj, variable, widget.v_model)
            
            msg += str(widget.v_model)
            output.add_msg(msg)
        
            return
        
        widget.on_event('change', partial(
            on_change,
            obj=obj,
            variable=variable, 
            output=self, 
            msg=msg
        ))
    
        return self
    
    def check_input(self, input_, msg=None):
        """
        Check if the inpupt value is initialized. If not return false and display an error message else return True
        
        Args:
            input_ : the input to check
            msg (str, optionnal): the message to display if the input is not set
            
        Returns:
            (bool): check if the value is initialized
        """
        if not msg: msg = "The value has not been initialized"
        init = True 
        
        if input_ == None:
            init = False
            self.add_msg(msg, 'error')
        
        return init
    

class Btn(v.Btn, SepalWidget):
    """
    Creates a process button filled with the provided text
    
    Returns: 
        btn (v.Btn) :
    """
    

    def __init__(self, text='Click', icon=None, **kwargs):
        super().__init__(**kwargs)
        self.color='primary'
        self.v_icon = None
        self.children=[text]
        
        if icon:
            self.set_icon(icon)

    def set_icon(self, icon):
        
        if self.v_icon:
            self.v_icon.children = [icon]
        else:
            self.v_icon = v.Icon(left=True, children=[icon])
            self.children = [self.v_icon] + self.children
            
        return self
        
    def toggle_loading(self):
        """disable and start loading or reverse"""
        self.loading = not self.loading
        self.disabled = self.loading
        
        return self

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
        
        def setTitle(self, title):
            """set the title in the appbar"""
            
            self.children = [
                self.toolBarButton, 
                v.ToolbarTitle(children=[title])
            ]
            
            return self
            
class DrawerItem(v.ListItem, SepalWidget):
    """create a drawer item using the user input"""
    
    def __init__(self, title, icon=None, card='', href='', **kwargs):
        
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
        
        if not href == '':
            self.href=href
            self.target="_blank"
        
        if not card == '':
            self._metadata = {'card_id': card }
            
    def display_tile(self, tiles):
        """
        display the apropriate tiles when the item is clicked
    
        Args:
            tiles ([v.Layout]) : the list of all the available tiles in the app
        """
        def on_click(widget, event, data, tiles):
            for tile in tiles:
                if widget._metadata['card_id'] == tile._metadata['mount_id']:
                    tile.show()
                else:
                    tile.hide()
    
        self.on_event('click', partial(on_click, tiles=tiles))
        
        return self
            
class NavDrawer(v.NavigationDrawer, SepalWidget):
        """ 
    create a navdrawer using the different items of the user and the sepal color framework. The drawer can include links to the github page of the project for wiki, bugs and repository.
    """
        
        def __init__(self, items, code=None, wiki=None, issue=None, **kwargs):
            
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
            def on_click(widget, event, data, drawer):
                drawer.v_model = not drawer.v_model
        
            toggleButton.on_event('click', partial(on_click, drawer=self))
                
            return self

class Footer(v.Footer, SepalWidget):
    """create a footer with cuzomizable text. Not yet capable of displaying logos"""
    def __init__(self, text="", **kwargs):
        
        text = text if text != '' else 'SEPAL \u00A9 {}'.format(datetime.date.today().year)
        
        super().__init__(
            color = sepal_main,
            class_ = "white--text",
            app=True,
            children = [text],
            **kwargs
        )
        
class App (v.App, SepalWidget):
        """Create an app display with the tiles created by the user. Display false footer and appBar if not filled. navdrawer is fully optionnal
        """
        
        def __init__(self, tiles=[''], appBar=None, footer=None, navDrawer=None, **kwargs):
            
            self.tiles = None if tiles == [''] else tiles
            
            app_children = []
            
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
            
            
class Tile(v.Layout, SepalWidget):
    """create a customizable tile for the sepal UI framework"""
    
    def __init__(self, id_, title, inputs=[''], btn=None, output=None, **kwargs):
        
        if btn:
            inputs.append(btn)
        
        if output:
            inputs.append(output)
        
        title = v.Html(xs12=True, tag='h2', children=[title])
        content = [v.Flex(xs12=True, children=[widget]) for widget in inputs]
        
        card = v.Card(
            class_ = "pa-5",
            raised = True,
            xs12 = True,
            children = [title] + content
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
        
    def set_content(self, content):
        
        self.children[0].children = [self.children[0].children[0]] + content
        
        return self 
    
    def set_title(self, title):
        
        title = v.Html(xs12=True, tag='h2', children=[title])
        
        self.children[0].children = [title] + self.children[0].children[1:]
        
        return self
        
    def hide(self):
        """hide the widget"""
        
        super().hide()
        
        if 'd-inline' in str(self.class_):
            self.class_ = self.class_.replace('d-inline','')
            
        return self
        
    def show(self):
        """ remove the d-none html class to the widget"""
        
        super().show()
        
        if not 'd-inline' in str(self.class_):
            self.class_ = str(self.class_).strip() + ' d-inline'
            
        return self
    
    def toggle_inputs(self, fields_2_show, fields):
        """
        display only the widgets that are part of the input_list. the widget_list is the list of all the widgets of the tile.
    
        Args:
            fields_2_show ([v.widget]) : the list of input to be display
            fields ([v.widget]) : the list of the tile widget
        """
    
        for field in fields:
            if field in fields_2_show: 
                if 'd-none' in str(field.class_):
                    field.class_ = field.class_.replace('d-none', '')
            else:
                if not 'd-none' in str(field.class_):
                    field.class_ = str(field.class_).strip() + ' d-none'

        return self
        
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
    
    def __init__(self, **kwargs):
        
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
    
    def __init__(self, text, path='#', **kwargs):
        
        #create the url
        if utils.is_absolute(path):
            url = path
        else: 
            url = utils.create_download_link(path)
        
        super().__init__(
            class_='ma-2',
            xs5=True,
            color='success',
            href=url,
            children=[
                v.Icon(left=True, children=['mdi-download']),
                text
            ],
            **kwargs
        )
        