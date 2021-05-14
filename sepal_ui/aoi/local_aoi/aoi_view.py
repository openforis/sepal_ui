import functools
from pathlib import Path
from traitlets import List, Any, link, observe, Unicode, HasTraits, Int
import json
from datetime import datetime as dt

import ipyvuetify as v
import pandas as pd
import geopandas as gpd
from shapely import geometry as sg

import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import utils as su
from sepal_ui.aoi.local_aoi.aoi_model import AoiModel
from sepal_ui.message import ms

CUSTOM = ms.aoi_sel.custom
ADMIN = ms.aoi_sel.administrative
ALL = 'All'

select_methods = {
    'ADMIN0': {'name': ms.aoi_sel.adm[0], 'type': ADMIN},
    'ADMIN1': {'name': ms.aoi_sel.adm[1], 'type': ADMIN},
    'ADMIN2': {'name': ms.aoi_sel.adm[2], 'type': ADMIN},
    'SHAPE': {'name': ms.aoi_sel.vector, 'type': CUSTOM},
    'DRAW': {'name': ms.aoi_sel.draw, 'type': CUSTOM},
    'POINTS': {'name': ms.aoi_sel.points, 'type': CUSTOM}
}
        
class Select(v.Select, sw.SepalWidget):
    """ A classic Vuetify Select widget inheriting from sepalwidgets"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class TextField(v.TextField, sw.SepalWidget):
    """ A classic Vuetify TextField widget inheriting from sepalwidgets"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class MethodSelect(Select):
    f"""
    A method selector. It will list the availabel methods for this very AoiView. 
    'ALL' will select all the available methods (default)
    'ADMIN' only the admin one, 'CUSTOM' only the custom one. 
    'XXX' will add the selected method to the list when '-XXX' will discard it. 
    You cannot mix adding and removing behaviours.
    
    Params:
        methods (str|[str]): a list of methods from the available list ({' '.join(select_methods.keys())})
    """
    
    def __init__(self, methods='ALL'):
        
        # create the method list
        if methods=='ALL':
            self.methods = select_methods
        elif methods == 'ADMIN':
            self.methods = {k: v for k, v in select_methods.items() if v['type'] == ADMIN}
        elif methods == 'CUSTOM':
            self.methods = {k: v for k, v in select_methods.items() if v['type'] == CUSTOM}
        elif type(methods) == list:
            
            if any(m[0] == '-' for m in methods) != all(m[0] == '-' for m in methods):
                raise Exception("You mixed adding and removing, punk")
            
            if methods[0][0] == '-':
                self.methods = select_methods
                [self.methods.pop(k[1:]) for k in methods]
            else:
                self.methods = {k: select_methods[k] for k in methods}
        else:
            raise Exception("I don't get what you meant")
            
        # build the item list with header 
        prev_type = None
        items = []
        for k, m in self.methods.items():
            current_type = m['type']
            
            if prev_type != current_type:
                items.append({'header': current_type})
            prev_type = current_type
            
            items.append({'text':m['name'], 'value': k})
            
        # create the input 
        super().__init__(label=ms.aoi_sel.method, items=items, v_model='', dense=True)
        
class AdminField(v.Select, sw.SepalWidget):
    
    # the file location of the database 
    GADM_FILE = Path(__file__).parents[2]/'scripts'/'gadm_database.csv'
    
    def __init__(self, level, parent=None, **kwargs):
        
        # get the level info 
        self.level = level
        self.parent = parent
        
        # init an empty widget
        self.v_model = None
        self.items = []
        self.clearable = True
        self.label = ms.aoi_sel.adm[level]
        super().__init__(**kwargs)
        
        # add js behaviour
        if self.parent:
            self.parent.observe(self._update, 'v_model')
            
    def show(self):
        """when an admin field is shown, show its parent as well"""
        
        super().show()
        
        if self.parent: self.parent.show()
        
        return self
            
    def get_items(self, filter_=None):
        """
        update the item list based on the given filter
        
        Params:
            filter_ (str): The GID code of the parent v_model to filter the current results
            
        Return:
            self
        """
        
        # extract the level list
        gadm_df = pd.read_csv(self.GADM_FILE).drop_duplicates(subset=f'GID_{self.level}')
        
        # filter it 
        if filter_: gadm_df = gadm_df[gadm_df[f'GID_{self.level-1}'] == filter_]
        
        # formatted as a item list for a select component
        self.items = [
            {
                'text': su.normalize_str(r[f'NAME_{self.level}'], folder=False), 
                'value': r[f'GID_{self.level}']
            } for _, r in gadm_df.iterrows()
        ] 
        
        return self
        
    def _update(self, change):
        """update the item list of the admin select"""
        
        # reset v_model
        self.v_model = None
        
        # update the items list
        if change['new']:
            self.get_items(change['new'])
            
        return self

class AoiView(v.Card):
    
    updated = Int(0).tag(sync=True)
    
    def __init__(self, methods='ALL', map_=None, *args, **kwargs):
        
        # get the model
        self.model = AoiModel(sw.Alert())
        
        # get the map if filled 
        self.map_=map_
        
        # create the method widget 
        self.w_method = MethodSelect(methods)
        
        # add the 6 methods blocks
        self.w_admin_0 = AdminField(0).get_items().hide()
        self.w_admin_1 = AdminField(1, self.w_admin_0).hide()
        self.w_admin_2 = AdminField(2, self.w_admin_1).hide()
        self.w_vector = sw.VectorField(label=ms.aoi_sel.vector).hide()
        self.w_points = sw.LoadTableField(label=ms.aoi_sel.points).hide()
        if self.map_: self.w_draw = TextField(label=ms.aoi_sel.aoi_name).hide()
        
        # group them together with the same key as the select_method object
        self.components = {
            'ADMIN0': self.w_admin_0,
            'ADMIN1': self.w_admin_1,
            'ADMIN2': self.w_admin_2,
            'SHAPE': self.w_vector,  
            'POINTS': self.w_points  
        }
        if self.map_: self.components['DRAW'] = self.w_draw
        
        # use the same alert as in the model
        self.alert = self.model.alert
        
        # bind the widgets to the model
        self.model \
            .bind(self.w_admin_0, 'admin') \
            .bind(self.w_admin_1, 'admin') \
            .bind(self.w_admin_2, 'admin') \
            .bind(self.w_vector, 'vector_json') \
            .bind(self.w_points, 'point_json') \
            .bind(self.w_method, 'method')
        if self.map_: self.model.bind(self.w_draw, 'name')
            
        # add a validation btn
        self.btn = sw.Btn(ms.aoi_sel.btn)
        
        # create the widget
        self.children = [self.w_method] + [*self.components.values()] + [self.btn, self.alert]
        
        super().__init__(*args, **kwargs)

        # Decorate methods
        # We have to decorate methods before declaring events, otherwise it will use the un-decorated method
        self._update_aoi = su.loading_button(button=self.btn, alert=self.alert, debug=True)(self._update_aoi)
        
        # js events
        self.w_method.observe(self._activate, 'v_model') # activate the appropriate widgets
        self.btn.on_event('click', self._update_aoi) # load the informations
        if self.map_: self.map_.dc.on_draw(self._handle_draw) # handle map drawing
            

    def _update_aoi(self, widget, event, data):
        """load the gdf in the model & update the map (if possible)"""
        
        # update the model 
        self.model.set_gdf()
        
        # update the map
        if self.map_:
            [self.map_.remove_layer(l) for l in self.map_.layers if l.name == 'aoi']
            self.map_.zoom_bounds(self.model.gdf.total_bounds)
            self.map_.add_layer(self.model.get_ipygeojson())
            self.map_.hide_dc()
        
        # tell the rest of the apps that the aoi have been updated 
        self.updated += 1
        
        return self
    
    def _activate(self, change):
        """activate the adapted widgets"""
        
        # clear and hide the alert 
        self.alert.reset()
        
        # deactivate or activate the dc
        if self.map_: self.map_.show_dc() if change['new'] == 'DRAW' else self.map_.hide_dc()
    
        # clear the inputs
        [w.reset() for w in self.components.values()]
        
        # activate the widget
        [w.show() if change['new'] == k else w.hide() for k, w in self.components.items()]
        
        return self
    
    def _handle_draw(self, target, action, geo_json):
        """handle the draw on map event"""
        
        # update the automatic name
        if not self.w_draw.v_model:
            self.w_draw.v_model = f'Manual_aoi_{dt.now().strftime("%Y-%m-%d_%H-%M-%S")}'
            
        # Init the json if it's not 
        if self.model.geo_json == None:
            self.model.geo_json = {'type': 'FeatureCollection', 'features': []}
        
        # polygonize circles 
        if 'radius' in geo_json['properties']['style']:
            geo_json = self.polygonize(geo_json)
        
        if action == 'created': # no edit as you don't know which one to change
            self.model.geo_json['features'].append(geo_json)
        elif action == 'deleted':
            self.model.geo_json['features'].remove(geo_json)
            
        return self
    
    @staticmethod
    def polygonize(geo_json):
        """
        Transform a ipyleaflet circle (a point with a radius) into a GeoJson multipolygon
        
        Params:
            geo_json (json): the circle geojson
            
        Return:
            (json): the polygonised circle
        """
        
        # get the input
        radius = geo_json['properties']['style']['radius']
        coordinates = geo_json['geometry']['coordinates']
        
        # create shapely point 
        circle = gpd.GeoSeries([sg.Point(coordinates)], crs=4326).to_crs(3857).buffer(radius).to_crs(4326)
        
        # insert it in the geo_json 
        json = geo_json
        json['geometry'] = circle[0].__geo_interface__
        
        return json