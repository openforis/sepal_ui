import functools
import os
import geopandas as gpd
import json
from pathlib import Path
from traitlets import Any, HasTraits
from ipyleaflet import GeoJSON


def catch_errors(alert):
    """Decorator to execute try/except sentence
    and catch errors in the alert message
    
    Params:
        alert (sw.Alert): Alert to display errors
    """
    def decorator_alert_error(func):
        @functools.wraps(func)
        def wrapper_alert_error(*args, **kwargs):
            try:
                value = func(*args, **kwargs)
            except Exception as e:
                alert.add_msg(f'{e}', type_='error')
                raise e
            return value
        return wrapper_alert_error
    return decorator_alert_error

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

        @catch_errors(self.alert)
        def process():
            file_path = Path(file)
            
            assert file_path.exists(), "File doesn't exists"
            
            if file_path.suffix == '.shp':

                self.gdf = gpd.read_file(str(file_path))
                self.gdf = self.gdf.to_crs("EPSG:4326")
        process()
            
    def gdf_to_ipygeojson(self):
        """ Converts current geopandas object into ipyleaflet GeoJSON"""
        
        @catch_errors(self.alert)
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
        