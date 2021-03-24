from functools import partial
from datetime import datetime

import ipyvuetify as v
from traitlets import (
    Unicode, observe, directional_link, List, 
    Bool
)

from sepal_ui.sepalwidgets.sepalwidget import SepalWidget, TYPES

class Divider(v.Divider, SepalWidget):
    """
    A custom Divider with the ability to dynamically change color
    Whenever the type\_ trait is modified, the divider class will change accordingly
    
    Args:
        class\_ (str, optional): the initial color of the divider 
        
    Attributes:
        type_ (str): the current color of the divider
    """
    # Added type_ trait to specify default divider color
    type_ = Unicode('').tag(sync=True)

    def __init__(self, class_='', **kwargs):
        self.class_ = class_
        super().__init__(**kwargs)

    @observe('type_')
    def add_class_type(self, change):
        """
        Change the color of the divider according to the type\_
        It is binded to the type\_ traitlet but can also be called manually
        
        Args:
            change (dict): the only useful key is 'new' which is the new required color
            
        Return: 
            self
        """
         
        type_= change['new']
        classes = self.class_.split(' ')
        existing = list(set(classes) & set(TYPES))
        if existing:
            classes[classes.index(existing[0])] = type_
            self.class_ = " ".join(classes)
        else:
            self.class_ += f' {type_}'
            
        return self
            
            
class Alert(v.Alert, SepalWidget):
    """
    A custom Alert widget. It is used as the output of all processes in the framework. 
    In the voila interfaces, print statement will not be displayed. 
    Instead use the sw.Alert method to provide information to the user.
    It's hidden by default.
    
    Args:
        type\_ (str, optional): The color of the Alert
    """
    
    def __init__(self, type_=None, **kwargs):

        self.text = True
        self.type = type_ if (type_ in TYPES) else TYPES[0]
        self.class_="mt-5"
        
        super().__init__(**kwargs)
    
        self.hide()
        
    def update_progress(self, progress, msg='Progress', bar_length=30):
        """
        Update the Alert message with a progress bar. This function will stay until we manage to use tqdm in the widgets
        
        Args:
            progress (float): the progress status in float [0, 1]
            msg (str, optionnal): The message to use before the progress bar 
            bar_length (int, optionnal): the length of the progress bar in characters 
            
        Return:
            self
        """
        
        # define the characters to use in the progress bar
        plain_char = '█'
        empty_char = ' '  
        
        # cast the progress to float
        progress = float(progress)
        if not (0 <= progress <= 1):
            raise ValueError(f"progress should be in [0, 1], {progress} given")
        
        # set the length parameter 
        block = int(round(bar_length * progress))

        # construct the message content
        text = f'|{plain_char * block + empty_char * (bar_length - block)}|'
    
        # add the message to the output
        self.add_live_msg(v.Html(
            tag='span', 
            children=[
                v.Html(tag='span', children=[f'{msg}: '], class_='d-inline'),
                v.Html(tag='pre', class_='info--text d-inline', children=[text]),
                v.Html(tag='span', children=[f' {progress *100:.1f}%'], class_='d-inline')
            ]
        ))
   
        return self
        
    def add_msg(self, msg, type_='info'):
        """
        Add a message in the alert by replacing all the existing one. 
        The color can also be changed dynamically
        
        Args:
            msg (str): the message to display
            type\_ (str, optional): the color to use in the widget
            
        Return:
            self
        """
        self.show()
        self.type = type_ if (type_ in TYPES) else TYPES[0]
        self.children = [v.Html(tag='p', children=[msg])]
        
        return self
        
    def add_live_msg(self, msg, type_='info'):
        """
        Add a message in the alert by replacing all the existing one. 
        Also add the timestamp of the display.
        The color can also be changed dynamically
        
        Args:
            msg (str): the message to display
            type\_ (str, optional): the color to use in the widget
            
        Return:
            self
        """
        
        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        self.show()
        self.type = type_ if (type_ in TYPES) else TYPES[0]
    
        self.children = [
            v.Html(tag='p', children=['[{}]'.format(current_time)]),
            v.Html(tag='p', children=[msg])
        ]
        
        return self

    def append_msg(self, msg, section=False):
        """ 
        Append a message in a new parragraph, with or without divider

        Args: 
            msg (str): the message to display
            section (bool, optional): add a Divider before the added message
            
        Return:
            self
        """
        
        self.show()
        
        if len(self.children):
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
        """ 
        Remove the last msg printed in the Aler widget
        
        Return:
            self
        """
        
        if len(self.children) > 1:
            current_children = self.children[:]
            self.children = current_children[:-1]
        else:
            self.reset()
            
        return self

    def reset(self):
        """
        Empty the messages and hide it
        
        Return:
            self
        """
        
        self.children = ['']
        self.hide()
        
        return self
    
    def bind(self, widget, obj, attribute, msg=None, verbose=True, secret=False):
        """ 
        Bind the attribute to the widget and display it in the alert.
        The binded input need to have an active `v_model` trait.
        After the binding, whenever the `v_model` of the input is changed, the io attribute is changed accordingly.
        The value can also be displayed in the alert with a custom message with the following format = `[custom message] + [v_model]`
    
        Args:
            widget (v.XX): an ipyvuetify input element with an activated `v_model` trait
            obj (io): any io object
            attribute (str): the name of the attribute in io object
            msg (str, optionnal): the output message displayed before the variable
            verbose (bool, optional): wheter the variable should be displayed to the user 
            secret (bool, optional): either if the variable is secret or not. If true only "*" will be shown in the output
            
        Return:
            self
        """
        if not msg: msg = 'The selected variable is: '
        
        def _on_change(change, obj=obj, attribute=attribute, msg=msg):
            
            # if the key doesn't exist the getattr function will raise an AttributeError
            getattr(obj, attribute)
            
            # change the obj value
            setattr(obj, attribute, change['new'])
            
            # add the message if needed
            if secret:
                msg += '*' * len(change['new'])
            else:
                msg += str(change['new'])
                
            if verbose:
                self.add_msg(msg)
        
            return
        
        widget.observe(_on_change, 'v_model')
        
        return self
    
    
    def check_input(self, input_, msg=None):
        """
        Check if the inpupt value is initialized. 
        If not return false and display an error message else return True
        
        Args:
            input\_ (any): the input to check
            msg (str, optionnal): the message to display if the input is not set
            
        Return:
            (bool): check if the value is initialized
        """
        if not msg: msg = "The value has not been initialized"
        init = True 
        
        # check the collection type that are the only one supporting the len method
        try:
            if len(input_) == 0:
                init = False
        except:
            if input_ == None:
                init = False
                
        if not init:
            self.add_msg(msg, 'error')
        
        return init
    
class StateBar(v.SystemBar):
    
    """ Widget to display quick messages on simple inline status bar
        
    Attributes:
        msg (Unicode): the msg to be displayed 
        done (Bool): State of bar, it will display a loading spin wheel if not done.
    
    """
    
    msg = Unicode('').tag(sync=True)
    done = Bool(False).tag(sync=True)
    
    def __init__(self,  **kwargs):
                        
        self.progress = v.ProgressCircular(
            indeterminate=not self.done,
            value=100,
            small=True,
            size=15,
            color='primary',
            class_='mr-2',
        )
        
        self.children = [self.progress, self.msg]
        
        super().__init__(**kwargs)
    
    @observe('done')
    def _change_done(self, change):
        """ Change progress wheel state"""
        self.progress.indeterminate = not self.done
            
    @observe('msg')
    def _change_msg(self, change):
        """ Change state bar message"""
        self.children = [self.progress, self.msg]
        
    def add_msg(self, msg, done=False):
        """ Change current status message"""
        self.msg = msg
        self.done = done
        
        return self