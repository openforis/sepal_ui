from traitlets import HasTraits, Any
import json

from ipywidgets import jsdlink, dlink

class Model(HasTraits):
    
    def __init__(self, traits=[], *args, **kwargs):
        
        # didn't manage to make it work and it seems dodgy has it creates a simlink to new class at each call
        #if len(traits):
        #    [self.add_traits(Any(val).tag(sync=True), label) for label, val in traits.items()]
                
        
        super().__init__(*args, **kwargs)
        
    def export_data(self):
        """
        Export a json description of all the object traitlets 
        Note that the members will be ignored
        
        Return:
            (dict): the serialized traitlets
        """
        
        return self.__dict__['_trait_values']
    
    def import_data(self, data):
        """
        Import the model (i.e. the traitlets) from a json file
        
        Params:
            json (dict): the json ditionary of the model
            
        Return:
            self
        """
        
        if type(data) == str:
            data = json.loads(data)
        
        for k, v in data.items():
            getattr(self, k) # to raise an error if the json is malformed 
            setattr(self, k, v)
            
    def bind(self, widget, trait):
        """
        Binding a widget input 'v_model' trait to a trait of the model. 
        The binding will be unidirectionnal for the sake of some custom widget that does not support it.
        This wrapper avoid to import the ipywidgets lib everywhere and reduce the number of parameters
        Some existence check are also performed and will throw an error if the trait doesn't exist
        
        Params:
            widget (v.widget): any input widget with a v_model trait
            trait (str): the name of a trait of the current model
            
        Return:
            self
        """
        
        # check trait existence 
        getattr(self, trait)
        
        # bind them 
        dlink((widget, 'v_model'),(self, trait))
        
        # maybe I would add the possiblity to add an alert to display stuff to the user with the same options as in alert.bind
        
        return self
        
        
        