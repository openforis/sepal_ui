import os
import json
from pathlib import Path
from traitlets import Any, HasTraits

import geopandas as gpd
from ipyleaflet import GeoJSON

from sepal_ui.scripts import utils as su

class AoiModel(HasTraits):
    
    country = Any('').tag(sync=True)

    def __init__(self, alert, *args, **kwargs):

        super().__init__(*args, **kwargs)
        
        self.alert = alert
        self.gdf = None
        self.ipygeojson = None
        self.selected_feature = None
        
    def shape_to_gpd(self, file):
        """ Converts shapefile into geopandas"""

        @su.catch_errors(self.alert)
        def process():
            file_path = Path(file)
            
            assert file_path.exists(), "File doesn't exists"
            
            if file_path.suffix == '.shp':

                self.gdf = gpd.read_file(str(file_path))
                self.gdf = self.gdf.to_crs("EPSG:4326")
        process()
            
    def gdf_to_ipygeojson(self):
        """ Converts current geopandas object into ipyleaflet GeoJSON"""
        
        @su.catch_errors(self.alert)
        def process():
            assert self.gdf is not None, "You must create a geopandas file before to convert it into GeoJSON"

            self.ipygeojson = GeoJSON(data=json.loads(self.gdf.to_json()))
        process()

    def geo_json_to_gdf(self, geo_json):
        """Converts drawn map features into geodataframe"""

        self.gdf = gpd.GeoDataFrame.from_features([geo_json])

    def _get_columns(self):
        """Return all columns skiping geometry"""
        return sorted(list(set(['geometry'])^set(self.gdf.columns.to_list())))
        
    def _get_fields(self, column):
        """Return fields from selected column"""
        return sorted(self.gdf[column].to_list())
    
    def _get_selected(self, column, field):
        """Get selected element"""
        
        return self.gdf[self.gdf[column] == field]
        