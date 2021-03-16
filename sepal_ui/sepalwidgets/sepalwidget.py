import ipyvuetify as v
from markdown import markdown
from traitlets import Unicode

TYPES = ('info', 'secondary', 'primary', 'error', 'warning', 'success', 'accent')

class SepalWidget(v.VuetifyWidget):
    """
    Custom vuetifyWidget to add specific methods
    
    Attributes:
        viz (bool): weather the file is displayed or not
        old_class (str): a saving attribute of the widget class
    """
    
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        
        self.viz = True
        self.old_class = ''
        
    def toggle_viz(self):
        """
        toogle the visibility of the widget
        
        Return:
            self
        """
        
        return self.hide() if self.viz else self.show()
    
    def hide(self):
        """
        Hide the widget by adding the d-none html class to the widget.
        Save the previous class and set viz attribute to False.
        
        Return:
            self
        """
        
        if not 'd-none' in str(self.class_):
            self.old_class = self.class_
            self.class_ = 'd-none'
            
        self.viz = False
        
        return self
        
    def show(self):
        """
        Hide the widget by removing the d-none html class to the widget
        Save the previous class and set viz attribute to True.
        
        Return:
            self
        """
        
        if self.old_class:
            self.class_ = self.old_class
        
        if 'd-none' in str(self.class_):
            self.class_ = str(self.class_).replace('d-none', '')
                
        self.viz = True
        
        return self
    
class Markdown(v.Layout, SepalWidget):
    """
    Custom Layout based on the markdown text given
    
    Args:
        mkd_str (str): the text to display using the markdown convention. multi-line string are also interpreted
    """
    
    def __init__(self, mkd_str="", **kwargs):
        
        mkd = markdown(mkd_str, extensions=['fenced_code','sane_lists'])
    
        #need to be nested in a div to be displayed
        mkd = '<div>\n' + mkd + '\n</div>'
    
        #create a Html widget
        class MyHTML(v.VuetifyTemplate):
            template = Unicode(mkd).tag(sync=True)
    
        content = MyHTML()
        
        super().__init__(
            row=True,
            class_='pa-5',
            align_center=True,
            children=[v.Flex(xs12=True, children=[content])],
            **kwargs
        )