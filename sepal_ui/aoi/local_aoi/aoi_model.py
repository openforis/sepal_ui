import json
from pathlib import Path
from traitlets import Any, HasTraits
from urllib.request import urlretrieve
import zipfile

import pandas as pd
import geopandas as gpd
from ipyleaflet import GeoJSON

from sepal_ui.scripts import utils as su

############################
###      parameters      ###
############################

# the base url to download gadm maps 
gadm_base_url = "https://biogeo.ucdavis.edu/data/gadm3.6/gpkg/gadm36_{}_gpkg.zip"

# the zip dir where we download the zips
gadm_zip_dir = Path('~', 'tmp', 'GADM_zip').expanduser()
gadm_zip_dir.mkdir(parents=True, exist_ok=True)

# the tmp dir with the geopackages
gadm_tmp_dir = Path('~', 'tmp', 'GADM').expanduser()
gadm_tmp_dir.mkdir(parents=True, exist_ok=True)

############################


class AoiModel(HasTraits):

    def __init__(self, alert, default_vector = None, default_admin=None, *args, **kwargs):

        super().__init__(*args, **kwargs)
        
        # keep the default informations in memory
        self.default_vector = default_vector
        self.default_admin = default_admin
        
        # selection parameters
        self.column = None
        self.field = None
        self.selected_feature = None
        self.json_csv = None # information that will be use to transform the csv into a gdf 
        self.admin = None
        
        # outputs of the selection 
        self.gdf = None
        self.ipygeojson = None
        self.selected_feature = None
        
        # the Alert used to display information
        self.alert = alert
        
        # set the default gdf in possible 
        if self.default_vector: 
            self.set_vector(default_vector)
        elif self.default_admin:
            self.set_admin(default_admin)
        
    def set_vector(self, vector_file):
        """
        set the model gdf according to a given vector_file. The gdf will be projected to EPSG:4326.
        The file need to be in one of the format compatible with the fiona library and/or GDAL/OGR.
        
        Params:
            vector_file(str, pathlib.path): the path to the vector file. The file type will be detected with the extension, please don't change it.
            
        Return:
            Self
        """
        
        # force cast to pathlib.Path
        vector_file = Path(vector_file)
            
        assert vector_file.is_file(), "File does not exist" # I think it's useless as the first test of read_file is to test existence
            
        self.gdf = gpd.read_file(vector_file).to_crs("EPSG:4326")
            
        return self
            
    def set_admin(self, admin):
        """
        Set the gdf according to given an administrative number in the GADM norm. The gdf will be projected in EPSG:4326
        
        Params:
            admin (str): an administrative GADM code from level 0 to 2
        
        Return:
            self
        """
        
        # save the country iso_code 
        iso_3 = admin[:3]
        
        # get the admin level corresponding to the given admin code
        gadm_file = Path(__file__).parents[2]/'scripts'/'gadm_database.csv'
        gadm_df = pd.read_csv(gadm_file)
        
        # extract the first element that include this administrative code and set the level accordingly 
        is_in = gadm_df.filter(['GID_0', 'GID_1', 'GID_2']).isin([admin])
        
        if not is_in.any().any():
            raise Exception("The code is not in the database")
        else:
            level = is_in[~((~is_in).all(axis=1))].idxmax(1).iloc[0][-1] # last character from 'GID_X' with X being the level
            
        # download the geopackage in tmp 
        file = gadm_tmp_dir/f'gadm36_{iso_3}.gpkg'
        zip_file = gadm_zip_dir/f'{iso_3}.zip'
        
        if not file.is_file():
            
            # get the zip from GADM server only the ISO_3 code need to be used
            urlretrieve(gadm_base_url.format(iso_3), zip_file)
            
            # extract all in a another tmp folder
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(gadm_tmp_dir)
            
        # read the geopackage 
        layer_name = f"gadm36_{iso_3}_{level}"
        level_gdf = gpd.read_file(file, layer=layer_name)
        
        # note that the runtime warning is normal for geopackages: https://stackoverflow.com/questions/64995369/geopandas-warning-on-read-file
        
        # get the exact admin from this layer 
        self.gdf = level_gdf[level_gdf[f'GID_{level}'] == admin]
        
        return self

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
        """Return fields from selected column."""
        
        return sorted(self.gdf[column].to_list())
    
    def _get_selected(self, column, field):
        """Get selected element"""
        
        return self.gdf[self.gdf[column] == field]
        