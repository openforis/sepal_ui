from pathlib import Path
from traitlets import Int
from datetime import datetime as dt

import ipyvuetify as v
import pandas as pd
import geopandas as gpd
from shapely import geometry as sg

import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import utils as su
from sepal_ui.aoi.aoi_model import AoiModel
from sepal_ui.message import ms
from sepal_ui import color as sc

CUSTOM = AoiModel.CUSTOM
ADMIN = AoiModel.ADMIN
ALL = 'All'
select_methods = AoiModel.METHODS

class Select(v.Select, sw.SepalWidget):
    """A classic Vuetify Select widget inheriting from sepalwidgets"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
class TextField(v.TextField, sw.SepalWidget):
    """ A classic Vuetify TextField widget inheriting from sepalwidgets"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
    
    def __init__(self, methods='ALL', gee=True):
        
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
                
                to_remove = [method[1:] for method in methods]
                
                # Rewrite the methods instead of mutate the class methods
                self.methods = {k:v for k,v in select_methods.items() if k not in to_remove} 
                
            else:
                self.methods = {k: select_methods[k] for k in methods}
        else:
            raise Exception("I don't get what you meant")
            
        if not gee:
            self.methods.pop('ASSET', None)
            
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
    """
    An admin level selector. It is binded to ee (GAUL 2015) or not (GADM 2021). allows to select administrative codes taking into account the administrative parent code and displaying humanly readable administrative names.
    
    Args:
        level (int): The administrative level of the field
        parent (AdminField): the adminField that deal with the parent admin level of the current selector. used to narrow down the possible options
        ee (bool, optional): wether to use ee or not (default to True)
        
    Attributes:
        gee (bool): the earthengine status
        level (int): the admin level of the current field
        parent (AdminField): the field parent object
    """
    
    # the file location of the database
    FILE = AoiModel.FILE
    CODE = AoiModel.CODE
    NAME = AoiModel.NAME
    
    def __init__(self, level, parent=None, gee=True, **kwargs):
        
        self.toto = "toto"
        
        # save ee state
        self.ee = gee
        
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
        """
        when an admin field is shown, show its parent as well
        
        Return:
            self
        """
        
        super().show()
        
        if self.parent: self.parent.show()
        
        return self
            
    def get_items(self, filter_=None):
        """
        update the item list based on the given filter
        
        Params:
            filter_ (str): The code of the parent v_model to filter the current results
            
        Return:
            self
        """
        
        # extract the level list
        df = pd.read_csv(self.FILE[self.ee]) \
            .drop_duplicates(subset=self.CODE[self.ee].format(self.level)) \
            .sort_values(self.NAME[self.ee].format(self.level))
        
        # filter it 
        if filter_: df = df[df[self.CODE[self.ee].format(self.level-1)] == filter_]
        
        # formatted as a item list for a select component
        self.items = [
            {
                'text': su.normalize_str(r[self.NAME[self.ee].format(self.level)], folder=False), 
                'value': r[self.CODE[self.ee].format(self.level)]
            } for _, r in df.iterrows()
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
    """
    Versatile card object to deal with the aoi selection. multiple selection method are available (see the MethodSelector object) and the widget can be fully customizable. Can also be bound to ee (ee==True) or not (ee==False)
    
    Args:
        methods (str, optional): the methods to use in the widget, default to 'ALL',
        map_ (SepalMap, optional): link the aoi_view to a custom SepalMap to display the output, default to None
        gee (bool, optional): wether to bind to ee or not
        vector (str|pathlib.Path, optional): the path to the default vector object
        admin (int, optional): the administrative code of the default selection. Need to be GADM if ee==False and GAUL 2015 if ee==True.
        asset (str, optional): the default asset. Can only work if ee==True
        
    Attributes:
        gee (bool): the earthengine binding status
        model (AoiModel): the aoiModel to save the aoi selected as gdf or ee.FeatureCollection
        map (SepalMap): the map if filled in the arguments
        w_method (MethodSelect): the the method selection widget
        w_admin_0, w_admin_1, w_admin2, w_vector, w_points, w_draw, w_asset (widgets): the selection widgets
        components (dict): the widgets stored in a dict using the method names as keys
        alert (sw.Alert): an alert component to display outputs
        btn (sw.Btn): a btn component
        
    """
    
    updated = Int(0).tag(sync=True)
    
    def __init__(self, methods='ALL', map_=None, gee=True, folder=None, **kwargs):
        
        # set ee dependencie
        self.ee = gee
        if gee: 
            su.init_ee()
            self.folder = folder
            
        # get the model   
        self.model = AoiModel(sw.Alert(), gee=gee, folder=folder, **kwargs)
        
        # get the map if filled 
        self.map_=map_
        
        # create the method widget 
        self.w_method = MethodSelect(methods, gee=gee)
        
        # add the 6 methods blocks
        self.w_admin_0 = AdminField(0, gee=gee).get_items().hide()
        self.w_admin_1 = AdminField(1, self.w_admin_0, gee=gee).hide()
        self.w_admin_2 = AdminField(2, self.w_admin_1, gee=gee).hide()
        self.w_vector = sw.VectorField(label=ms.aoi_sel.vector).hide()
        self.w_points = sw.LoadTableField(label=ms.aoi_sel.points).hide()
        if self.map_: self.w_draw = TextField(label=ms.aoi_sel.aoi_name).hide()
        if self.ee: self.w_asset = sw.AssetSelect(label=ms.aoi_sel.asset, folder=self.folder, types=['TABLE']).hide()
        
        # group them together with the same key as the select_method object
        self.components = {
            'ADMIN0': self.w_admin_0,
            'ADMIN1': self.w_admin_1,
            'ADMIN2': self.w_admin_2,
            'SHAPE': self.w_vector,  
            'POINTS': self.w_points  
        }
        if self.map_: self.components['DRAW'] = self.w_draw
        if self.ee: self.components['ASSET'] = self.w_asset
        
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
        if self.ee: self.model.bind(self.w_asset, 'asset_name')
            
        # add a validation btn
        self.btn = sw.Btn(ms.aoi_sel.btn)
        
        # create the widget
        self.children = [self.w_method] + [*self.components.values()] + [self.btn, self.alert]
        
        super().__init__(**kwargs)
        
        # js events
        self.w_method.observe(self._activate, 'v_model') # activate the appropriate widgets
        self.btn.on_event('click', self._update_aoi) # load the informations
        if self.map_: self.map_.dc.on_draw(self._handle_draw) # handle map drawing
            
    @su.loading_button(debug=False)
    def _update_aoi(self, widget, event, data):
        """load the object in the model & update the map (if possible)"""
        
        # update the model 
        self.model.set_object()
        
        # update the map
        if self.map_:
            [self.map_.remove_layer(l) for l in self.map_.layers if l.name == 'aoi']
            self.map_.zoom_bounds(self.model.total_bounds())
            
            if self.ee:
                self.map_.addLayer(self.model.feature_collection, {'color': sc.success}, 'aoi')
            else:
                self.map_.add_layer(self.model.get_ipygeojson())
                
            self.map_.hide_dc()
        
        # tell the rest of the apps that the aoi have been updated 
        self.updated += 1
        
        return self
    
    def reset(self):
        """clear the aoi_model from input and remove the layer from the map (if existing)"""
        
        # clear the map
        if self.map_:
            [self.map_.remove_layer(l) for l in self.map_.layers if l.name == 'aoi']
            #self.map_.center = [0, 0]
            #self.map_.zoom = 3
            
        # clear the model
        self.model.clear_attributes()
        
        # reset the alert 
        self.alert.reset()
        
        # reset the view of the widgets 
        self.w_method.v_model = None
        
        return self
            
        
    
    def _activate(self, change):
        """activate the adapted widgets"""
        
        # clear and hide the alert 
        self.alert.reset()
        
        # deactivate or activate the dc
        # clear the geo_json saved features to start from scratch
        if self.map_:
            if change['new'] == 'DRAW': 
                self.map_.show_dc()
                self.model.geo_json = None
            else:
                self.map_.hide_dc()
            
    
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