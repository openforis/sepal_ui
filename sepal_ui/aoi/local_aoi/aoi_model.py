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

# the file location of the database 
gadm_file = Path(__file__).parents[2]/'scripts'/'gadm_database.csv'

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
        self.json_csv = None # information that will be use to transform the csv into a gdf
        self.json_vector = None # information that will be use to transform the vector file into a gdf 
        self.admin = None
        self.name = None # the name of the file (use only in drawed shaped)
        
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
        self.default_admin = default_admin
        
        # set the default gdf in possible 
        if self.default_vector: 
            self.set_vector(default_vector)
        elif self.default_admin:
            self.set_admin(default_admin)
            
        return self
        
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
        
        # set the name using the file stem
        self.name = su.normalize_str(vector_file.stem)
            
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
            
        return bool(self.admin)
    
    def clear_attributes(self):
        """
        Return all attributes to their default state.
        Set the default setting as current gdf.

        Return: 
            self
        """

        # keep the default 
        default_admin = self.default_admi
        default_vector = self.default_vector 

        # delete all the attributes
        [setattr(self, attr, None) for attr in self.__dict__.keys()]

        # reset the default 
        self.set_default(default_vector, default_admin)

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
        