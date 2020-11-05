from functools import partial
from datetime import datetime

import ipyvuetify as v
from traitlets import Unicode, observe, directional_link, List

from .sepalwidget import SepalWidget, TYPES

class Divider(v.Divider, SepalWidget):

    # Added type_ trait to specify default divider color
    type_ = Unicode('').tag(sync=True)

    def __init__(self, class_='', **kwargs):
        self.class_= class_
        super().__init__(**kwargs)

    @observe('type_')
    def add_class_type(self, change):

        type_= change['new']
        classes = self.class_.split(' ')
        existing = list(set(classes) & set(TYPES))
        if existing:
            classes[classes.index(existing[0])] = type_
            self.class_ = " ".join(classes)
        else:
            self.class_ += f' {type_}'
            
        return
            
            
class Alert(v.Alert, SepalWidget):
    """create an alert widget that can be used to display the process outputs"""
    
    def __init__(self, type_=None, **kwargs):
        
        type_ = type_ if (type_ in TYPES) else TYPES[0]
        
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
        self.type = type_ if (type_ in TYPES) else TYPES[0]
        self.children = [v.Html(tag='p', children=[msg])]
        
        return self
        
    
    def add_live_msg(self, msg, type_='info'):
        
        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        self.show()
        self.type = type_ if (type_ in TYPES) else TYPES[0]
    
        self.children = [
            v.Html(tag='p', children=['[{}]'.format(current_time)]),
            v.Html(tag='p', children=[msg])
        ]
        
        return self

    def append_msg(self, msg, section=False):
        """ Append a message in a new parragraph

        Args: 
            msg (text): Text to display
            section (boolean): Append message with section Divider
        """
        self.show()
        if self.children[0]:
            current_children = self.children[:]
            if section:
                # As the list is mutable, and the trait is only triggered when
                # the children is changed, so have to create a copy.
                divider = Divider(class_='my-4', style='opacity: 0.22')

                # link Alert type with divider type
                directional_link((self, 'type'), (divider, 'type_'))
                current_children.extend([
                    divider,
                    v.Html(tag='p', children=[msg])
                ])
                self.children = current_children

            else:
                current_children.append(
                    v.Html(tag='p', children=[msg])
                )
                self.children = current_children
        else:
            self.add_msg(msg)
            
        return self


    def remove_last_msg(self):

        if self.children[0]:
            current_children = self.children[:]
            self.children = current_children[:-1]
        else:
            self.reset()
            
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
        
        def on_change(change, obj=obj, variable=variable, msg=msg):
        
            setattr(obj, variable, change['new'])
            
            msg += str(change['new'])
            self.add_msg(msg)
        
            return
        
        widget.observe(on_change, 'v_model')
        
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