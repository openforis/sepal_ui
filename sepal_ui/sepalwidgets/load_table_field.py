import json

import pandas as pd
import ipyvuetify as v 
from ipywidgets import jslink
from sepal_ui import sepalwidgets as sw

class LoadTableField(v.Col, sw.SepalWidget):
    
    def __init__(self):
        
        self.fileInput = sw.FileInput(['.csv'])
                
        self.IdSelect = self._LocalSelect('id_column', 'Id')
        self.LngSelect = self._LocalSelect('lng_column', 'Longitude')
        self.LatSelect = self._LocalSelect('lat_column', 'Latitude')
        
        
        default_v_model = {
            'pathname'  : None, 
            'id_column' : None, 
            'lat_column': None, 
            'lng_column': None
        }
        
        super().__init__(
            v_model = json.dumps(default_v_model),
            children = [
                self.fileInput,
                self.IdSelect,
                self.LngSelect,
                self.LatSelect
            ]
        )
        
        # link the dropdowns
        jslink((self.IdSelect, 'items'),(self.LngSelect, 'items'))
        jslink((self.IdSelect, 'items'),(self.LatSelect, 'items'))
        
        # link the widget with v_model 
        self.fileInput.observe(self.__on_file_input_change, 'v_model')
        self.IdSelect.observe(self.__on_select_change, 'v_model')
        self.LngSelect.observe(self.__on_select_change, 'v_model')
        self.LatSelect.observe(self.__on_select_change, 'v_model')
        
    def __on_file_input_change(self, change):
        
        path = change['new']
        df = pd.read_csv(path)
        
        if len(df.columns) < 3: return 
        
        self.__set_value('pathname', path)
        
        # clear the selects
        self.IdSelect.items = df.columns.tolist()
        self.__clear_select()
        
        # pre load values that sounds like what we are looking for 
        # it will only keep the first occurence of each one 
        for name in reversed(df.columns.tolist()):
            lname = name.lower() 
            if 'id' in lname:
                self.IdSelect.v_model = name
            elif any(ext in lname for ext in ['lng', 'long', 'longitude', 'x_coord', 'xcoord']):
                self.LngSelect.v_model = name
            elif any(ext in lname for ext in ['lat', 'latitude', 'y_coord', 'ycoord']):
                self.LatSelect.v_model = name
                
    def __clear_select(self):
        """clear the select v_model"""
        self.IdSelect.v_model = self.LngSelect.v_model = self.LatSelect.v_model = None
        
        return 
    
    def __on_select_change(self, change):
        
        name = change['owner']._metadata['name']
        self.__set_value(name, change['new'])
        
        return
        
    def __set_value(self, name, value):
        
        """ set the value in the json dictionary"""
        tmp = json.loads(self.v_model)
        tmp[name] = value
        self.v_model = json.dumps(tmp)
        
        return
    
    def get_v_model(self):
        """get the v_model as a dict"""
        return json.loads(self.v_model)
    
    def get_pathname(self):
        """return the pathname from v_model"""
        return json.loads(self.v_model)['pathname']
    
    def get_id_lbl(self):
        """return the id column label from v_model"""
        return json.loads(self.v_model)['id_column']
    
    def get_lng_lbl(self):
        """return the longitude column label from v_model"""
        return json.loads(self.v_model)['lng_column']
    
    def get_lat_lbl(self):
        """return the latitude column label from v_model"""
        return json.loads(self.v_model)['lat_column']
    
    
    class _LocalSelect(v.Select):
            
            def __init__(self, metadata, label):
                
                super().__init__(
                    _metadata = {'name': metadata}, 
                    items     = [], 
                    label     = label, 
                    v_model   = None
                )
        