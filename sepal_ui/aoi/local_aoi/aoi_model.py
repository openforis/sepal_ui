import json
from pathlib import Path
from traitlets import Any, HasTraits
from urllib.request import urlretrieve
import zipfile

import pandas as pd
import geopandas as gpd
from ipyleaflet import GeoJSON
import ipyvuetify as v

from sepal_ui.scripts import utils as su
from sepal_ui.message import ms
from sepal_ui.model import Model

############################
###      parameters      ###
############################

# I don't really know where to put them ... in the beggining of the class maybe ?

# the file location of the database 
gadm_file = Path(__file__).parents[2]/'scripts'/'gadm_database.csv'

# the base url to download gadm maps 
gadm_base_url = "https://biogeo.ucdavis.edu/data/gadm3.6/gpkg/gadm36_{}_gpkg.zip"

# the zip dir where we download the zips
gadm_zip_dir = Path('~', 'tmp', 'GADM_zip').expanduser()
gadm_zip_dir.mkdir(parents=True, exist_ok=True)

# default styling of the layer
aoi_style = {
    "stroke": True,
    "color": v.theme.themes.dark.success,
    "weight": 2,
    "opacity": 1,
    "fill": True,
    "fillColor": v.theme.themes.dark.success,
    "fillOpacity": 0.4,
}
############################


class AoiModel(Model):
    
    # widget related traitlets
    default_vector = Any(None).tag(sync=True)
    default_admin = Any(None).tag(syn=True)
    point_json = Any(None).tag(sync=True) # information that will be use to transform the csv into a gdf
    vector_json = Any(None).tag(sync=True) # information that will be use to transform the vector file into a gdf
    geo_json = Any({'type': 'FeatureCollection', 'features': []}).tag(sync=True) # the drawn geojson featureCollection
    admin = Any(None).tag(sync=True)
    name = Any(None).tag(sync=True) # the name of the file (use only in drawn shaped)

    def __init__(self, alert, default_vector = None, default_admin=None, *args, **kwargs):

        super().__init__(*args, **kwargs)
        
        # selection parameters
        #self.point_json = None # information that will be use to transform the csv into a gdf
        #self.vector_json = None # information that will be use to transform the vector file into a gdf
        #self.geo_json = {'type': 'FeatureCollection', 'features': []} # the drawn geojson featureCollection
        #self.admin = None
        #self.name = None # the name of the file (use only in drawn shaped)
        
        # outputs of the selection
        self.gdf = None
        self.ipygeojson = None
        self.selected_feature = None
        
        # the Alert used to display information
        self.alert = alert
        
        # set default values
        self.set_default(default_vector, default_admin)
        
        
    def set_default(self, default_vector=None, default_admin=None):
        """
        Set the default value of the object and create a gdf out of it
        
        Params:
            default_vector (str, pathlib.path): the default vector file that will be used to produce the gdf. need to be readable by fiona and/or GDAL/OGR
            default_admin (str): the default administrative area in GADM norm
            
        Return:
            self
        """
        
        # save the default values
        self.default_vector = default_vector
        self.vector_json = {'pathname': str(default_vector), 'column': None, 'value': None} if default_vector else None
        self.default_admin = self.admin = default_admin
        
        # set the default gdf in possible 
        if (self.vector_json != None) or (self.admin != None):
            self.set_gdf()
            
        return self
    
    def set_gdf(self):
        """
        set the gdf based on the model inputs
        
        Return:
            self
        """
        
        # there should be a more pythonic way of doing the same thing
        if self.admin:
            self._from_admin(self.admin)
        elif self.point_json['pathname']:
            self._from_points(self.point_json)
        elif self.vector_json['pathname']:
            self._from_vector(self.vector_json)
        elif len(self.geo_json['features']):
            self._from_geo_json(self.geo_json)
        else:
            raise Exception(ms.aoi_sel.no_inputs)
            
        self.alert.add_msg(ms.aoi_sel.complete, "success")
        
        return self
    
    def get_ipygeojson(self):
        """ 
        Converts current geopandas object into ipyleaflet GeoJSON
        
        Return: 
            (GeoJSON): the geojson layer of the aoi gdf
        """
        
        if type(self.gdf) == type(None):
            raise Exception("You must set the gdf before converting it into GeoJSON")
    
        data = json.loads(self.gdf.to_json())
        self.ipygeojson = GeoJSON(data=data, style=aoi_style, name='aoi')
        
        return self.ipygeojson
    
    def _from_points(self, point_json):
        """set the gdf output from a csv json"""
        
        # cast the pathname to pathlib Path
        point_file = Path(point_json['pathname'])
    
        # check that the columns are well set 
        values = [v for v in point_json.values()]
        if not len(values) == len(set(values)):
            raise Exception(ms.aoi_sel.duplicate_key)
    
        # create the gdf
        df = pd.read_csv(point_file, sep=None, engine='python')
        self.gdf = gpd.GeoDataFrame(df, crs='EPSG:4326', geometry = gpd.points_from_xy(df[point_json['lng_column']], df[point_json['lat_column']]))
        
        # set the name
        self.name = point_file.stem
        
        return self
    
    def _from_vector(self, vector_json):
        """set the gdf output from a vector json"""
        
        # cast the pathname to pathlib Path
        vector_file = Path(vector_json['pathname'])
        
        # create the gdf
        self.gdf = gpd.read_file(vector_file).to_crs("EPSG:4326")
        
        # filter it if necessary
        if vector_json['value']:
            self.gdf = self.gdf[self.gdf[vector_json['column']] == vector_json['value']]
        
        # set the name using the file stem
        self.name = vector_file.stem
        
        return self
    
    def _from_geo_json(self, geo_json):
        """set the gdf output from a geo_json"""
        
        # create the gdf
        self.gdf = gpd.GeoDataFrame.from_features(geo_json)
        
        # save the geojson in downloads 
        path = Path('~', 'downloads', 'aoi').expanduser()
        path.mkdir(exist_ok=True, parents=True) # if nothing have been run the downloads folder doesn't exist
        self.gdf.to_file(path/f'{self.name}.geojson', driver='GeoJSON')
        
        return self
            
    def _from_admin(self, admin):
        """Set the gdf according to given an administrative number in the GADM norm. The gdf will be projected in EPSG:4326"""
        
        # save the country iso_code 
        iso_3 = admin[:3]
        
        # get the admin level corresponding to the given admin code
        gadm_df = pd.read_csv(gadm_file)
        
        # extract the first element that include this administrative code and set the level accordingly 
        is_in = gadm_df.filter(['GID_0', 'GID_1', 'GID_2']).isin([admin])
        
        if not is_in.any().any():
            raise Exception("The code is not in the database")
        else:
            level = is_in[~((~is_in).all(axis=1))].idxmax(1).iloc[0][-1] # last character from 'GID_X' with X being the level
            
        # download the geopackage in tmp 
        zip_file = gadm_zip_dir/f'{iso_3}.zip'
        
        if not zip_file.is_file():
            
            # get the zip from GADM server only the ISO_3 code need to be used
            urlretrieve(gadm_base_url.format(iso_3), zip_file)
            
        # read the geopackage 
        layer_name = f"gadm36_{iso_3}_{level}"
        level_gdf = gpd.read_file(f'{zip_file}!gadm36_{iso_3}.gpkg', layer=layer_name)
        
        # note that the runtime warning is normal for geopackages: https://stackoverflow.com/questions/64995369/geopandas-warning-on-read-file
        
        # get the exact admin from this layer 
        self.gdf = level_gdf[level_gdf[f'GID_{level}'] == admin]
        
        # set the name using the layer 
        r = self.gdf.iloc[0]
        names = [su.normalize_str(r[f'NAME_{i}']) if i else r['GID_0'] for i in range(int(level)+1)]
        self.name = '_'.join(names)
        
        return self
    
    def is_admin(self):
        """
        Test if the current object is refeering to an administrative layer or not
        
        Return:
            (bool): True if administrative layer else False. False as well if no aoi is selected.
        """
        
        # It may seem useless at the moment but When we'll need to name the aoi (for output files and folder) I think it will become handy
        return bool(self.admin)
    
    def clear_attributes(self):
        """
        Return all attributes to their default state.
        Set the default setting as current gdf.

        Return: 
            self
        """

        # keep the default 
        default_admin = self.default_admin
        default_vector = self.default_vector 

        # delete all the traits
        [setattr(self, attr, None) for attr in self.trait_names()]
        
        # reset the FeatureCollection 
        self.geo_json = {'type': 'FeatureCollection', 'features': []}

        # reset the default 
        self.set_default(default_vector, default_admin)
        
        # reset the outputs
        self.gdf = None
        self.ipygeojson = None
        self.selected_feature = None

        return self

    def _get_columns(self):
        """Return all columns skiping geometry"""
        
        # they were used to build the model but I think we can keep it as a way to interact with the model 
        
        return sorted(list(set(['geometry'])^set(self.gdf.columns.to_list())))
        
    def _get_fields(self, column):
        """Return fields from selected column."""
        
        # they were used to build the model but I think we can keep it as a way to interact with the model 
        
        return sorted(self.gdf[column].to_list())
    
    def _get_selected(self, column, field):
        """Get selected element"""
        
        # they were used to build the model but I think we can keep it as a way to interact with the model 
        
        return self.gdf[self.gdf[column] == field]
        