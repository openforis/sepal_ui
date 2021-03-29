import os
import geopandas as gpd
import json

from pathlib import Path
from traitlets import (
    Unicode, link, observe
)
import ipyvuetify as v
import sepal_ui.sepalwidgets as sw

class AOI(v.Layout):
    
    shapefile = Unicode('').tag(sync=True)
    
    def __init__(self, statebar=None, **kwargs):
    
        super().__init__(**kwargs)
        
        self.gdf = None
        
        # Parameters
        self.out_path = Path('')
        self.json_path = None
        
        # Widgets
        self.shape_input = sw.FileInput(['.shp'], os.getcwd())
        
        self.w_state_bar = sw.StateBar(loading=True) if not statebar else statebar
        
        # Link behaviours 
        
        link((self.shape_input, 'file'), (self, 'shapefile'))
        
        # View
        
        self.children=[
            v.Layout(row=True, children=[
                self.shape_input,
            ])
        ]
        
        # Add a statebar if there is not provided an external one
        if not statebar: self.children = self.children + [self.w_state_bar]

    @observe('shapefile')
    def shape_to_geojson(self, change):
        """ Converts shapefile into Json file"""
        
        shp_file_path = Path(self.shapefile)
        if shp_file_path.suffix == '.shp':

            self.gdf = gpd.read_file(str(shp_file_path))
            self.gdf = self.gdf.to_crs("EPSG:4326")
            
            self.json_path = shp_file_path.parent/f'{shp_file_path.stem}.geojson'
            
            if not self.json_path.exists():
                self.w_state_bar.add_msg('Converting shape to GeoJSON', loading=False)
                self.gdf.to_file(str(self.json_path), driver='GeoJSON')
                self.w_state_bar.add_msg('Done', loading=True)
            else:
                self.w_state_bar.add_msg('Geojson file already created', loading=True)
                
    def get_ipyleaflet_geojson(self):
        """Returns GeoJSON ipyleaflet object from Json file"""
        
        if self.json_path:
            self.w_state_bar.add_msg('Converting shape to GeoJSON', loading=False)
            with open(self.json_path) as f:
                data = json.load(f)        
                ipygeojson = GeoJSON(
                    data=data,
                    name=self.json_path.stem, 
                    style={'color': 'green', 'fillOpacity': 0, 'weight': 3})

            self.w_state_bar.add_msg('Done', loading=True)
        
            return ipygeojson
        else:
            self.w_state_bar.add_msg('There is not a shapefile selected.', loading=True)