import ipyvuetify as v
import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import utils as su

from traitlets import (
    List, Any, link, observe, Unicode, HasTraits
)

from .aoi_model import AoiModel

ALL = 'All'

class Flex(v.Flex, sw.SepalWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
class Select(v.Select, sw.SepalWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
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
    
    method = Unicode('').tag(sync=True)
    column = Any('').tag(sync=True)
    field = Any('').tag(sync=True)
    
    def __init__(self, map_=None, *args, **kwargs):
        
        self.map_=map_
        self.methods = self._get_methods()
        self.column_field = ColumnField()
        
        self.alert = sw.Alert()
        self.model = AoiModel(self.alert)
        
        w_method = v.Select(
            label = 'Select a method',
            v_model = self.method,
            items = self._get_methods()
        )
        
        self.w_countries = v.Select(
            label="Select country",
            v_model='',
            items=self._get_countries(),
        )
        self.btn_country = sw.Btn('Select', small=True)
        
        w_countries_btn = Flex(
            class_='d-flex align-center mb-2',
            row=True, 
            children=[self.w_countries, self.btn_country])
        
        
        self.w_file = sw.FileInput(
            ['.shp'], 
            '/home/dguerrero/restoration_viewer/shp/'
        )
        
        self.btn_file = sw.Btn('Select file', small=True)
        w_file_btn = Flex(
            class_='d-flex align-center mb-2',
            row=True, 
            children=[self.w_file, self.btn_file])
        
        w_file_btn = Flex(
            class_='d-flex align-center mb-2',
            row=True, 
            children=[self.w_file, self.btn_file]
        )
        
        self.components = {
            'Country' : w_countries_btn,
            'Upload file' : w_file_btn,
            'Column_field' : self.column_field,
        }
        
        self._hide_components()
        
        super().__init__(*args, **kwargs)
        
        
        # Link traits view
        link((self, 'method'),(w_method, 'v_model'))
        link((self, 'column'),(self.column_field.w_column, 'v_model'))
        link((self, 'field'),(self.column_field.w_field, 'v_model'))
        
        # Link traits with model
        link((self.model, 'country'),(self.w_countries, 'v_model'))
        
        # Events
        self.btn_file.on_event('click', self._file_btn_event)
        # On drawing control events
        self.map_.dc.on_draw(self.handle_draw)
        
        self.children=[
            self.alert,
            w_method,
            w_countries_btn,
            w_file_btn,
            self.column_field,
        ]
            
        
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
    
    @observe('column')
    def _get_fields(self, change):
        """Populate widget field items with fields"""
        
        # Reset fields items
        self.column_field.items = []
        
        if self.column == ALL:
            "All geometries were selected"
        else:
            self.column_field.w_field.loading=True
            self.column_field.field_items = self.model._get_fields(self.column)
            self.column_field.w_field.loading=False
    
    @observe('field')
    def _get_selected_feature(self, change):
        """Define selected feature with the current options"""

        self.model.selected_feature = self.model._get_selected(
            self.column, self.field)
        
        self.model.selected_feature = self.model._get_selected(
            self.column, self.field)
        
        if self.map_:
            self.zoom_and_center(self.model.selected_feature)

    def _hide_components(self):
        """Hide all possible componentes"""
        
        for component in self.components.values():
            su.hide_component(component)
        
    def _get_methods(self):
        """Handle which methods will be displayed in select widget"""
        
        return ['Draw on map', 'Country', 'Upload file']
    
    def _get_countries(self):
        """Create a list of countries"""
        
        return list(range(10))


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