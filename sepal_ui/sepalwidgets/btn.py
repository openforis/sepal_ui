import ipyvuetify as v 

from sepal_ui.sepalwidgets.sepalwidget import SepalWidget
from ..scripts import utils

class Btn(v.Btn, SepalWidget):
    """
    Custom process Btn filled with the provided text.
    the color will be defaulted to 'primary' and can be changed afterward according to your need
    
    Args:
        text (str, optional): the text to display in the btn
        icon (str, optional): the full name of any mdi-icon
        
    Attributes:
        v_icon (v.icon): the icon in the btn
    """
    
    def __init__(self, text='Click', icon=None, **kwargs):

        self.color='primary'
        self.v_icon = None
        self.children=[text]
        
        if icon:
            self.set_icon(icon)
        
        super().__init__(**kwargs)
        


    def set_icon(self, icon):
        """
        set a new icon
        
        Args:
            icon (str): the full name of a mdi-icon
            
        Return:
            self
        """
        if self.v_icon:
            self.v_icon.children = [icon]
        else:
            self.v_icon = v.Icon(left=True, children=[icon])
            self.children = [self.v_icon] + self.children
            
        return self
        
    def toggle_loading(self):
        """
        Jump between to states : disabled and loading - enabled and not loading
        
        Return:
            self
        """
        self.loading = not self.loading
        self.disabled = self.loading
        
        return self
    
class DownloadBtn(v.Btn, SepalWidget):
    """
    Custom download Btn filled with the provided text.
    the download icon is automatically embeded and green.
    The btn only accepts absolute links. if non is provided then the btn stays disabled
    
    Args:
        text (str): the message inside the btn
        path (str, optional): the absolute to a downloadable content    
    """
    
    def __init__(self, text, path='#', **kwargs):
        
        self.class_   = 'ma-2'
        self.xs5      = True
        self.color    = 'success'
        self.children = [
            v.Icon(left=True, children=['mdi-download']),
            text
        ]
        super().__init__(**kwargs)
        
        # create the url 
        self.set_url(path)
        
    def set_url(self, path='#'):
        """
        Set the url of the download btn. and unable it. 
        If nothing is provided the btn is disabled
        
        Args:
            path (str): the absolute path to a downloadable content
            
        Return:
            self
        """
        
        if utils.is_absolute(path):
            url = path
        else: 
            url = utils.create_download_link(path)
            
        self.href = url
        self.disabled = (path =='#')
        
        return self