import ipyvuetify as v 

from .sepalwidget import SepalWidget
from ..scripts import utils

class Btn(v.Btn, SepalWidget):
    """Creates a process button filled with the provided text"""
    
    def __init__(self, text='Click', icon=None, **kwargs):
        super().__init__(**kwargs)
        self.color='primary'
        self.v_icon = None
        self.children=[text]
        
        if icon:
            self.set_icon(icon)

    def set_icon(self, icon):
        """set the icon for the btn"""
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