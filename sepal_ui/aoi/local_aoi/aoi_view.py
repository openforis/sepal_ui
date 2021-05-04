import functools
from pathlib import Path
from traitlets import List, Any, link, observe, Unicode, HasTraits
import json

import ipyvuetify as v
import pandas as pd
import geopandas as gpd

import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import utils as su
from sepal_ui.aoi.local_aoi.aoi_model import AoiModel
from sepal_ui.message import ms

CUSTOM = 'custom'
ADMIN = 'admin'
ALL = 'All'

select_methods = {
    'ADMIN0': {'name': 'admin 0', 'type': ADMIN},
    'ADMIN1': {'name': 'admin 1', 'type': ADMIN},
    'ADMIN2': {'name': 'admin 2', 'type': ADMIN},
    'SHAPE': {'name': 'vector shape', 'type': CUSTOM},
    'DRAW': {'name': 'draw a shape', 'type': CUSTOM},
    'POINTS': {'name': 'use point file', 'type': CUSTOM}
}

class Flex(v.Flex, sw.SepalWidget):
    """ A classic Vuetify Flex widget inheriting from sepalwidgets"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
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
        super().__init__(label=ms.aoi_sel.method_lbl, items=items, v_model=None, dense=True)
        
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
        self.items = [{'text': su.normalize_str(r[f'NAME_{self.level}']), 'value': r[f'GID_{self.level}']} for _, r in gadm_df.iterrows()] 
        
        return self
        
    def _update(self, change):
        """update the item list of the admin select"""
        
        # reset v_model
        self.v_model = None
        
        # update the items list
        if change['new']:
            self.get_items(change['new'])
            
        return self
            
def loading_button(button):
    """Decorator to execute try/except sentence
    and toggle loading button object
    
    Params:
        button (sw.Btn): Toggle button
    """
    def decorator_loading(func):
        @functools.wraps(func)
        def wrapper_loading(*args, **kwargs):
            button.loading=True
            try:
                value = func(*args, **kwargs)
            except Exception as e:
                button.loading=False
            button.loading=False
            return value
        return wrapper_loading
    return decorator_loading
        
class ColumnField(v.Flex, sw.SepalWidget):
    
    column_items = List([]).tag(sync=True)
    field_items = List([]).tag(sync=True)
    
    ALL_ITEMS = [{'text':'Use all features', 'value':ALL}, {'divider':True}]
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args,**kwargs)
        
        self.w_column = Select(
            _metadata={'name':'column'},
            label="Filter by column",
            v_model=ALL,
            items=self.column_items
        )
        
        self.w_field = Select(
            _metadata={'name':'field'},
            label="Select field",
            v_model="",
            items=self.field_items
        ).hide()
        
        self.children=[
            self.w_column,
            self.w_field
        ]
        
        # Link traits
        link((self, 'field_items'),(self.w_field, 'items'))
        
        # Events
        self.w_column.observe(self.toggle_fields, 'v_model')
    
    def toggle_fields(self, change):
        """Toggle field widget"""
        self.w_field.show() if change['new'] != ALL else self.w_field.hide()
        
    @observe('column_items')
    def _add_all_item(self, change):
        """Add 'All' item to the columns items as the first option"""
        self.w_column.items =  self.ALL_ITEMS + change['new']
        
    def reset(self):
        """Reset items to its original state"""
        self.column_items = self.field_items = []

class AoiView(v.Card):
    
    #method = Unicode('').tag(sync=True)
    #column = Any('').tag(sync=True)
    #field = Any('').tag(sync=True)
    
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
        self.w_vector = sw.VectorField() .hide()
        self.w_points = sw.LoadTableField().hide()
        if self.map_: self.w_draw = TextField(label="aoi name").hide()
        
        # group them together with the same key as the select_method object
        self.components = {
            'ADMIN0': self.w_admin_0,
            'ADMIN1': self.w_admin_1,
            'ADMIN2': self.w_admin_2,
            'SHAPE': self.w_vector,  
            'POINTS': self.w_points  
        }
        if self.map_: self.components['DRAW'] = self.w_draw
        
        # create an alert to bind to the model 
        # I would like to integrate the binding directly to the Model object (https://github.com/12rambau/sepal_ui/issues/198)
        self.alert = self.model.alert \
            .bind(self.w_admin_0, self.model, 'admin') \
            .bind(self.w_admin_1, self.model, 'admin') \
            .bind(self.w_admin_2, self.model, 'admin') \
            .bind(self.w_vector, self.model, 'vector_json') \
            .bind(self.w_points, self.model, 'point_json') 
        if self.map_: self.alert.bind(self.w_draw, self.model, 'name')
        
        # add a validation btn
        self.btn = sw.Btn()
        
        # create the widget
        self.children = [self.w_method] + [*self.components.values()] + [self.btn, self.alert.show()]
        super().__init__(*args, **kwargs)
        
        # js events
        self.w_method.observe(self._activate, 'v_model') # activate the appropriate widgets
        # load the informations
        # handle map drawing
        
        
        
        
        #self.column_field = ColumnField()
        
        
        #self.w_countries = v.Select(
        #    label="Select country",
        #    v_model='',
        #    items=self._get_countries(),
        #)
        #self.btn_country = sw.Btn('Select', small=True)
        
        #w_countries_btn = Flex(
        #    class_='d-flex align-center mb-2',
        #    row=True, 
        #    children=[self.w_countries, self.btn_country])
        
        
        #self.w_file = sw.FileInput(['.shp'])
        
        #self.btn_file = sw.Btn('Select file', small=True)

        #w_file_btn = Flex(
        #    class_='d-flex align-center mb-2',
        #    row=True, 
        #    children=[self.w_file, self.btn_file])
        
        #w_file_btn = Flex(
        #    class_='d-flex align-center mb-2',
        #    row=True, 
        #    children=[self.w_file, self.btn_file]
        #)
        
        #self.components = {
        #    'Country' : w_countries_btn,
        #    'Upload file' : w_file_btn,
        #    'Column_field' : self.column_field,
        #}
        
        #self._hide_components()
        
        #super().__init__(*args, **kwargs)
        
        
        # Link traits view
        #link((self, 'method'),(w_method, 'v_model'))
        #link((self, 'column'),(self.column_field.w_column, 'v_model'))
        #link((self, 'field'),(self.column_field.w_field, 'v_model'))
        
        # Link traits with model
        #link((self.model, 'country'),(self.w_countries, 'v_model'))
        
        # Events
        #self.btn_file.on_event('click', self._file_btn_event)
        # On drawing control events
        #self.map_.dc.on_draw(self.handle_draw)
        
        #self.children=[
        #    self.w_method,
        #    self.w_vector,
        #    self.w_points,
        #    self.w_draw,
        #    self.w_admin_0,
        #    self.w_admin_1,
        #    self.w_admin_2,
        #    #w_countries_btn,
        #    #w_file_btn,
        #    #self.column_field,
        #    self.alert,
        #]
        
    def _activate(self, change):
        """activate the adapted widgets"""
        
        # deactivate or activate the dc
        if self.map_: self.m.show_dc() if change['new'] == 'DRAW' else self.m.hide_dc()
            
        # clear the inputs
        for w in self.components.values(): w.v_model = None
         
        # activate the widget
        [w.show() if change['new'] == k else w.hide() for k, w in self.components.items()]
        
        return self
        
    def zoom_and_center(self, layer):
        """Add layers to the map"""
        
        minx, miny, maxx, maxy = list(layer.total_bounds)
        
        # Center map to the centroid of the layer(s)
        self.map_.center = [(maxy-miny)/2+miny, (maxx-minx)/2+minx]
        
        # zoom to bounds
        bounds = [(maxy,minx), (miny,minx), (maxy,maxx), (miny,maxx)]
        self.map_.zoom_bounds(bounds=bounds, zoom_out=0);


    def _file_btn_event(self, widget, event, data):
        """Define behavior when the file button is clicked"""

        @loading_button(self.btn_file)
        def event():
            self.remove_layers()
            self.column_field.reset()
            
            # Create a geopandas dataset
            self.model.shape_to_gpd(self.w_file.file)
            
            # Display vector file into map_
            if self.map_:
                self.model.gdf_to_ipygeojson()
                self.zoom_and_center(self.model.gdf)
                self.map_.add_layer(self.model.ipygeojson)


            # Populate columns widget with all columsn plus 'ALL' in case user 
            # wants to use all 
            self.column_field.column_items = self.model._get_columns()
            
            # Show column-field widget
            self.column_field.show()
        event()
    
    #@observe('column')
    #def _get_fields(self, change):
    #    """Populate widget field items with fields"""
    #    
    #    # Reset fields items
    #    self.column_field.items = []
    #    
    #    if self.column == ALL:
    #        "All geometries were selected"
    #    else:
    #        self.column_field.w_field.loading=True
    #        self.column_field.field_items = self.model._get_fields(self.column)
    #        self.column_field.w_field.loading=False
    #
    #@observe('field')
    #def _get_selected_feature(self, change):
    #    """Define selected feature with the current options"""
    #
    #    self.model.selected_feature = self.model._get_selected(
    #        self.column, self.field)
    #    
    #    self.model.selected_feature = self.model._get_selected(
    #        self.column, self.field)
    #    
    #    if self.map_:
    #        self.zoom_and_center(self.model.selected_feature)

    #def _hide_components(self):
    #    """Hide all possible componentes"""
    #    
    #    for component in self.components.values():
    #        su.hide_component(component)

    def remove_layers(self):
        """Remove all loaded layers"""

        # get map layers
        layers = self.map_.layers
        
        # loop and remove layers 
        [self.map_.remove_last_layer() for _ in range(len(layers))]


    @observe('method')
    def _aoi_method_event(self, change):
        
        method = change['new']

        # Remove layers from map
        self.remove_layers()

        # Hide components
        self._hide_components()
        
        if method == 'Draw on map':
            self.map_.show_dc()
        else:
            self.map_.hide_dc()
            su.show_component(self.components[method])

    def handle_draw(self, target, action, geo_json):

        if action in ['created', 'edited']:
            self.model.geo_json_to_gdf(geo_json)