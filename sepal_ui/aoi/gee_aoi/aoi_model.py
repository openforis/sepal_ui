from pathlib import Path
from traitlets import Any

import pandas as pd 
import geopandas as gpd
import ee
import geemap

from sepal_ui.model import Model
from sepal_ui.scripts import utils as su
from sepal_ui.scripts import gee
from sepal_ui.message import ms

class AoiModel(Model):
    
    # const params 
    GAUL_FILE = Path(__file__).parent[2]/'scripts'/'gaul_database.csv' # the file location of the GAUL dataset
    ASSET_SUFFIX = 'aoi_' # the suffix to identify the asset in GEE
    GAUL_ASSET = "FAO/GAUL/2015/level{}"
    
    # model traits 
    method = Any(None).tag(sync=True)
    
    default_asset = Any(None).tag(sync=True)
    default_admin = Any(None).tag(sync=True)
    
    point_json = Any(None).tag(sync=True) # information that will be use to transform the csv into a gdf
    vector_json = Any(None).tag(sync=True) # information that will be use to transform the vector file into a gdf
    geo_json = Any(None).tag(sync=True) # the drawn geojson featureCollection
    admin = Any(None).tag(sync=True) # the gaul admin number
    asset_name = Any(None).tag(sync=True) # the asset name
    
    name = Any(None).tag(sync=True) # the name of the file (use only in drawn shaped)
    
    
    @su.need_ee
    def __init__(self, alert, default_asset=None, default_admin=None, folder=None, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        # debug params 
        self.folder = folder or ee.data.getAssetRoots()[0]['id']
        
        # output of the selection 
        self.feature_collection = None
        self.selected_feature = None
        
        # the Alert used to display information 
        self.alert = alert
        
        # set the default values 
        self.set_default(default_asset, default_admin)
        
    def set_default(self, default_asset=None, default_admin=None):
        """
        Set the default value of the object and create a gfeature collection out of it
        
        Params:
            default_asset (str): the default asset name, need to point to a readable FeatureCollection
            default_admin (str): the default administrative area in GAUl norm
            
        Return:
            self
        """
        
        # save the default values
        self.default_asset = self.asset_name = default_asset
        self.default_admin = self.admin = default_admin
        
        # set the default gdf in possible 
        if self.asset_name != None:
            self.set_feature_collection('ASSET')
        elif self.admin != None:
            self.set_feature_collection('ADMIN0')
            
        return self 
    
    def set_feature_collection(self, method=None):
        """
        set the ee.FeatureCollection based on the model inputs.The method can be manually overwrite
        
        Args:
            method (str| optional): a model method
        
        Return:
            self
        """
        # overwrite self.method
        self.method = method or self.method
        
        if self.method in ['ADMIN0', 'ADMIN1', 'ADMIN2']:
            self._from_admin(self.admin)
        elif self.method == 'POINTS':
            self._from_points(self.point_json)
        elif self.method == 'SHAPE':
            self._from_vector(self.vector_json)
        elif self.method == 'DRAW':
            self._from_geo_json(self.geo_json)
        elif self.method == 'ASSET':
            self._from_asset(self.asset_name)
        else:
            raise Exception(ms.aoi_sel.no_inputs)
            
        self.alert.add_msg(ms.aoi_sel.complete, "success")
        
        return self
    
    def _from_asset(self, asset_name):
        """set the ee.FeatureCollection output from an existing asset"""
        
        # check that I have access to the asset 
        ee_col = ee.FeatureCollection(asset_name)
        ee_col.geometry().bounds().coordinates().get(0).getInfo() # it will raise and error if we cannot access the asset
        
        # set the feature collection 
        self.feature_collection = ee_col 
        
        # set the name 
        self.name = Path(asset_name).stem.replace(self.ASSET_SUFFIX, '')
        
        return self
    
    def _from_points(self, point_json):
        """set the ee.FeatureCollection output from a csv json"""
        
        if not all(point_json.values()):
            raise Exception('All fields are required, please fill them.')
            
        # cast the pathname to pathlib Path
        point_file = Path(point_json['pathname'])
    
        # check that the columns are well set 
        values = [v for v in point_json.values()]
        if not len(values) == len(set(values)):
            raise Exception(ms.aoi_sel.duplicate_key)
    
        # create the gdf
        df = pd.read_csv(point_file, sep=None, engine='python')
        gdf = gpd.GeoDataFrame(
            df, 
            crs='EPSG:4326', 
            geometry = gpd.points_from_xy(
                df[point_json['lng_column']], 
                df[point_json['lat_column']])
        )
        
        # transform the gdf to ee.FeatureCollection 
        self.feature_collection = geemap.geojson_to_ee(gdf.__geo_interface__)
        
        # set the name
        self.name = point_file.stem
        
        # export as a GEE asset
        self.export_to_asset()
        
        return self    
    
    def _from_vector(self, vector_json):
        """set the ee.FeatureCollection output from a vector json"""
        
        if not (vector_json['pathname']):
            raise Exception('Please select a file.')
        
        if vector_json['column'] != 'ALL':
            if vector_json['value'] is None:
                raise Exception('Please select a value.')
            
        # cast the pathname to pathlib Path
        vector_file = Path(vector_json['pathname'])
        
        # create the gdf
        gdf = gpd.read_file(vector_file).to_crs("EPSG:4326")
        
        # set the name using the file stem
        self.name = vector_file.stem
        
        # filter it if necessary
        if vector_json['value']:
            gdf = gdf[gdf[vector_json['column']] == vector_json['value']]
            self.name = f"{self.name}_{vector_json['column']}_{vector_json['value']}"
            
        # transform the gdf to ee.FeatureCollection 
        self.feature_collection = geemap.geojson_to_ee(gdf.__geo_interface__)
        
        # export as a GEE asset
        self.export_to_asset()
        
        return self
    
    def _from_geo_json(self, geo_json):
        """set the ee.FeatureCollection output from a geo_json"""
        
        if not geo_json:
            raise Exception('Please draw a shape in the map')
        
        # create the gdf
        gdf = gpd.GeoDataFrame.from_features(geo_json)
        
        # normalize the name
        self.name =su.normalize_str(self.name)
        
        # transform the gdf to ee.FeatureCollection 
        self.feature_collection = geemap.geojson_to_ee(gdf.__geo_interface__)
        
        # export as a GEE asset
        self.export_to_asset()
        
        return self
            
    def _from_admin(self, admin):
        
        """Set the ee.FeatureCollection according to given an administrative number in the GAUL norm. The gdf will be projected in EPSG:4326"""
        
        if not admin:
            raise Exception('Select an administrative layer')
            
        # save the country iso_code 
        iso_3 = admin[:3]
        
        # get the admin level corresponding to the given admin code
        gaul_df = pd.read_csv(self.GAUL_FILE)
        
        # extract the first element that include this administrative code and set the level accordingly 
        is_in = gaul_df.filter(['ADM0_CODE', 'ADM1_CODE', 'ADM2_CODE']).isin([admin])
        
        if not is_in.any().any():
            raise Exception("The code is not in the database")
        else:
            level = is_in[~((~is_in).all(axis=1))].idxmax(1).iloc[0][3] # 4th character from 'ADMX_CODE' with X being the level
            
        # get the feature_collection
        self.feature_collection = ee.FeatureCollection(self.GAUL_ASSET.format(level)).filter(ee.Filter.eq(f'ADM{level}_CODE', admin))
        
        # name the model 
        r = gaul_df[gaul_df[f'ADM{level}_CODE'] == admin].iloc[0]
        names = [su.normalize_str(r[f'ADM{i}_NAME']) if i else r['alpha-3'] for i in range(int(level)+1)]
        self.name = '_'.join(names)
        
        return self
    
    def clear_attributes(self):
        """
        Return all attributes to their default state.
        Set the default setting as current feature_collection.

        Return: 
            self
        """

        # keep the default 
        default_admin = self.default_admin
        default_asset = self.default_asset 

        # delete all the traits
        [setattr(self, attr, None) for attr in self.trait_names()]
        
        # reset the outputs
        self.feature_collection = None
        self.selected_feature = None

        # reset the default 
        self.set_default(default_asset, default_admin)

        return self

    def get_columns(self):
        """Return all columns skiping geometry""" 
        
        if type(self.gdf) == type(None):
            raise Exception("You must set the gdf before interacting with it")
        
        return sorted(list(set(['geometry'])^set(self.gdf.columns.to_list())))
        
    def get_fields(self, column):
        """Return fields from selected column."""
        
        if type(self.gdf) == type(None):
            raise Exception("You must set the gdf before interacting with it")
        
        return sorted(self.gdf[column].to_list())
    
    def get_selected(self, column, field):
        """Get selected element"""
        
        if type(self.gdf) == type(None):
            raise Exception("You must set the gdf before interacting with it") 
        
        return self.gdf[self.gdf[column] == field]
    
    def export_to_asset(self):
        """Export the feature_collection as an asset"""
        
        asset_name = self.ASSET_SUFFIX + self.name
        asset_id = str(Path(self.folder, asset_name))
        
        # check if the table already exist
        if asset_id in [a['name'] for a in gee.get_assets(self.folder)]:
            return self
        
        # check if the task is running 
        if gee.is_running(asset_name):
            return self
        
        # run the task
        task_config = {
            'collection': self.feature_collection,
            'description': asset_name,
            'assetId': asset_id
        }
        
        task = ee.batch.Export.table.toAsset(**task_config)
        task.start()
        
        return self
    
    def get_columns(self):
        """ 
        Retrieve the columns or variables from self excluding `system:index` and `Shape_Area`.

        Return: 
            ([str]): sorted list cof column names
        """
        
        aoi_ee = ee.Feature(self.feature_collection.first())
        columns = aoi_ee.propertyNames().getInfo()
        return sorted([col for col in columns if col not in ['system:index', 'Shape_Area']])
    
    def get_fields(self, column):
        """" 
        Retrieve the fields from a column
        
        Args:
            column (str): A column name to query over the asset
        
        Return: 
            ([str]): sorted list of fields value

        """
        fields = self.feature_collection.distinct(column).aggregate_array(column)
        return sorted(fields.getInfo())
    
    def get_selected_feature(self, column, field):
        """ 
        Select an ee object based on selected column and field.

        Return:
            (ee.Feature): the Feature associated with the query
        """
        
        self.selected_feature = self.feature_collection.filterMetadata(column, 'equals', field)

        return self.selected_feature
        
    def total_bounds(self):
        """Reproduce the behaviour of the total_bounds method from geopandas
        Return the minxx, miny, maxx, maxy values
        """
        
        ee_bounds = self.feature_collection.geometry().bounds().coordinates()
        coords = ee_bounds.get(0).getInfo()
        ll, ur = coords[0], coords[2]

        # Get the bounding box
        return ll[0], ll[1], ur[0], ur[1]
        
        
        