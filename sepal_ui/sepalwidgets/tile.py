import os 
from markdown import markdown
from traitlets import Unicode

import ipyvuetify as v

from sepal_ui.sepalwidgets.sepalwidget import SepalWidget
from sepal_ui.scripts import utils as su

class Tile(v.Layout, SepalWidget):
    """
    Custom Layout widget for the sepal UI framework. 
    It an helper to build a consistent tiling system. 
    Tile objects are indeed compatible with the other classes from sepal_ui.
    
    Args:
        id_ (str): the tile id that will be written in its mount_id _metadata attribute
        title (str): the title of the Tile
        inputs ([list]): the list of widget to display inside the tile
        btn (v.Btn): the process btn
        output (sw.Alert): the alert to display process informations to the end user
    """
    
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
        
    def set_content(self, inputs):
        """
        Replace the current content of the tile with the provided inputs
        DO NOT USE, refactoring needed
        
        Args:
            inputs ([list]): the list of widget to display inside the tile
            
        Return:
            self
        """
        
        content = [v.Flex(xs12=True, children=[widget]) for widget in inputs]
        self.children[0].children = [self.children[0].children[0]] + content
        
        return self 
    
    def set_title(self, title):
        """
        Replace the current title
        
        Args:
            title (str): the new title of the object
            
        Return:
            self
        """
        
        title = v.Html(xs12=True, tag='h2', children=[title])
        
        self.children[0].children = [title] + self.children[0].children[1:]
        
        return self
    
    def get_title(self):
        """
        Return the current title of the tile
        
        Return:
            (str): the title
        """ 
        
        return self.children[0].children[0].children[0]
    
    def toggle_inputs(self, fields_2_show, fields):
        """
        Display only the widgets that are part of the input_list. the widget_list is the list of all the widgets of the tile.
    
        Args:
            fields_2_show ([v.widget]) : the list of input to be display
            fields ([v.widget]) : the list of the tile widget
            
        Return:
            self
        """
    
        for field in fields:
            if field in fields_2_show:
                su.show_component(field)
            else:
                su.hide_component(field)
                    
        return self
    
    def get_id(self):
        """
        Return the mount_id value
        
        Return:
            (str): the moun_id value from _metadata dict
        """
        
        return self._metadata['mount_id']
        
class TileAbout(Tile):
    """
    Create an about tile using a .md file. 
    This tile will have the "about_widget" id and "About" title.
    
    Args:
        pathname (str | pathlib.Path): the path to the .md file
    """
    
    def __init__(self, pathname, **kwargs):
        
        #read the content and transform it into a html
        with open(pathname, 'r') as f:
            about = f.read()
        
        about = markdown(about, extensions=['fenced_code','sane_lists'])
    
        #need to be nested in a div to be displayed
        about = '<div>\n' + about + '\n</div>'
    
        #create a Html widget
        class MyHTML(v.VuetifyTemplate):
            template = Unicode(about).tag(sync=True)
    
    
        content = MyHTML()
        
        super().__init__('about_widget', 'About', inputs=[content], **kwargs)
        
class TileDisclaimer(Tile):
    """
    Create a about tile using a the generic disclaimer .md file. 
    This tile will have the "about_widget" id and "Disclaimer" title.
    """
    
    def __init__(self, **kwargs):
        
        pathname = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'disclaimer.md')
        
        #read the content and transform it into a html
        with open(pathname, 'r') as f:
            about = f.read()
        
        about = markdown(about, extensions=['fenced_code','sane_lists'])
    
        #need to be nested in a div to be displayed
        about = '<div>\n' + about + '\n</div>'
    
        #create a Html widget
        class MyHTML(v.VuetifyTemplate):
            template = Unicode(about).tag(sync=True)
    
    
        content = MyHTML()
        
        super().__init__('about_widget', 'Disclaimer', inputs=[content], **kwargs)