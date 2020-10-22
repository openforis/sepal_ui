import ipyvuetify as v
from markdown import markdown
from traitlets import Unicode

TYPES = ('info', 'secondary', 'primary', 'error', 'warning', 'success')

class SepalWidget(v.VuetifyWidget):
    
    
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        self.viz = True
        self.old_class = ''
        
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
            self.old_class = self.class_
            self.class_ = 'd-none'
            
        self.viz = False
        
        return self
        
    def show(self):
        """ remove the d-none html class to the widget"""
        if self.old_class:
            self.class_ = self.old_class
        else:
            if 'd-none' in str(self.class_):
                self.class_ = str(self.class_).replace('d-none', '')
        self.viz = True
        
        return self
    
class Markdown(v.Layout, SepalWidget):
    """create a v.layout based on the markdown text given"""
    
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