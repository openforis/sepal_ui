#!/usr/bin/env python3

import ipyvuetify as v

class SepalWidget(v.VuetifyWidget):
    
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        self.class_ = "mt-5"
    
    def hide(self):
        """add the d-none html class to the widget"""
        if not 'd-none' in self.class_:
            self.class_ = self.class_.strip() + ' d-none'
        
    def show(self):
        """ remove the d-none html class to the widget"""
        if 'd-none' in self.class_:
            self.class_ = self.class_.replace('d-none', '')

class Alert(v.Alert, SepalWidget):
    
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
    

    def __init__(self, text='Button', icon =None, **kwargs):
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

    def disable(self):
        self.disabled = True
        
    def activate(self):
        self.loading = False
        self.disabled = False
        
    def on_loading(self):
        self.loading = True