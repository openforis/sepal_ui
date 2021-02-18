from pathlib import Path

import ee
import geemap
import shapely.geometry as sg
import geopandas as gpd
import ipyvuetify as v 

from sepal_ui.scripts import utils as su
    
# initialize earth engine
su.init_ee()

class Aoi_io:
    """
    an io object dedicated to the sorage and the manipulation of aoi. 
    It is meant to be used with the TileAoi object. 
    By using this you will be able to provide your application with aoi as an ee_object or any other intersting format.
    The class also provide insight on your aoi.
    
    Args: 
        alert_widget (sw.Alert): an alert output to display message when computing stuff internally. This is a legacy parameter
        default_asset (str): the default asset to use when no others are provided
        
    Attributes:
        default_asset (str): the default asset link
        
        assetId (str): the assetId of the current asset
        column (str): name of a aoi's column (feature)  
        field (str): name or value of a specific filed in a specific column
        selected_feature (ee.Feature): a feature queried inside the ee.FeatureCollection version of the object
        json_csv (str | pathlib.Path): the path to the json initial file
        country_code (int): the code of the country in FAUL GAUL 2015 format
        feature_collection (ee.FeatureCollection): the feature_collection to use as asset when dealing with administrative layers
        
        file_input (str | pathlib.Path): the path to the input .shp file
        file_name (str): the name that will be used to name the AOI when exporting
        country_selection (str): the name of the country being used 
        selection_method (str): the selection method used in the linked aoi.TileAoi
        drawn_feat (geo_json): the feature drawn on the map
        alert (sw.Alert): the alert to display message
    """
    
    def __init__(self, alert_widget=None, default_asset=None):
        
        # keep the default asset in memory
        self.default_asset = default_asset
        
        # GEE parameters
        self.assetId = self.default_asset
        self.column = None
        self.field = None
        self.selected_feature = None
        self.json_csv = None # information that will be use to transform the csv into asset 
        self.country_code = None # to name the asset coming from country selection
        self.feature_collection = None # to access the country asset

        #set up your inputs
        self.file_input = None
        self.file_name = None
        self.country_selection = None
        self.selection_method = None
        self.drawn_feat = None
        self.alert = alert_widget
        
    def is_admin(self):
        """
        Test if the current aoi_io object is refeering to an administrative layer or not
        
        Return:
            (bool): True if administrative layer else False. False as well if no aoi is selected.
        """
        admin = False
        
        if self.country_code:
            admin = True
            
        return admin
        
    def get_aoi_ee(self):
        """ 
        get the ee_object corresponding to current self, None if no aoi set.
            
        Return:
            (ee.FeatureCollection): the aoi FeatureCollection in GEE format
        """
        
        obj = None
        if self.is_admin():
            obj = self.feature_collection
        elif self.assetId:
            obj = ee.FeatureCollection(self.assetId)
            
        return obj
    
    def get_columns(self):
        """ 
        Retrieve the columns or variables from self excluding `system:index` and `Shape_Area`.

            Return: 
                ([str]): sorted list cof column names
        """
        
        aoi_ee = self.get_aoi_ee()
        columns = ee.Feature(aoi_ee.first()).propertyNames().getInfo()
        columns = sorted([col for col in columns if col not in ['system:index', 'Shape_Area']])
        
        return columns
    
    def get_fields(self, column=None):
        """" 
        Retrieve the fields from a column. It will use the self.column if not provided.
        
        Args:
            column (str, optional): A column name to query over the asset
        
        Return: 
            ([str]): sorted list of fields value

        """
        
        if not column:
            column = self.column

        aoi_ee = self.get_aoi_ee()
        fields = sorted(aoi_ee.distinct(column).aggregate_array(column).getInfo())

        return fields

    def get_selected_feature(self):
        """ 
        Select an ee object based on the current `self.column` and `self.field`.

        Return:
            (ee.Geometry): the geometry associated with the query
        """

        if not self.column or not self.field:
            raise Exception('You must first select a column and a field.')

        ee_asset = self.get_aoi_ee()
        select_feature = ee_asset.filterMetadata(self.column, 'equals', self.field).geometry()

        # Specify the selected feature
        self.selected_feature = select_feature

        return select_feature

    def clear_selected(self):
        """
        clear the selected_feature attribute.
        
        Return:
            self
        """
        self.selected_feature = None
        
        return self

    def clear_attributes(self):
        """
        Return all attributes to their default state.
        Set the default_asset as current assetId.
        
        Return: 
            self
        """

        # GEE parameters
        self.assetId = self.default_asset
        self.column = None
        self.field = None
        self.selected_feature = None
        self.json_csv = None
        self.country_code = None
        self.feature_collection = None

        # set up your inputs
        self.file_input = None
        self.file_name = None
        self.country_selection = None
        self.selection_method = None
        self.drawn_feat = None

        return self
    
    def get_not_null_attrs(self):
        """
        Retrieve all the non null attributes of the object.
        
        Return:
            ([str]): The list of the non null attributes' name
        """
        attrs = dict((k, v) for k, v in self.__dict__.items() if v is not None)
        
        return attrs

    def display_on_map(self, map_):
        """ 
        Display the current aoi on a `ms.SepalMap`.
        The drawing control of the map will be removed if existing.

        Args:
            map_ (ms.SepalMap): Map to display the element
            
        Return:
            self
        """
        aoi = self.get_aoi_ee()
        map_.zoom_ee_object(aoi.geometry())
        map_.addLayer(aoi, {'color': v.theme.themes.dark.success}, name='aoi')
        
        map_.hide_dc()
        
        return self


    def get_bounds(self, ee_object, cardinal=False):
        """ 
        Get the min(lon,lat) and max(lon, lat) from the given `ee` object.
        returns coordinates (lon, lat) of each cardinal points (tl, bl, tr, br) if cardinal is `True` else returns a bounding box (min_lon, min_lat, max_lon, max_lat)

        Args:
            ee_asset (ee.object): GEE asset (FeatureCollection, Geometry or str)
            cardinal (boolean) (optional)

        Return:
            (tuple(tuple(int)) | tuple(int)): coordinates (lon, lat) of each cardinal points or a bounding box
        """ 
            
        ee_bounds = ee.FeatureCollection(ee_object).geometry().bounds().coordinates()
        coords = ee_bounds.get(0).getInfo()
        ll, ur = coords[0], coords[2]

        # Get the bounding box
        min_lon, min_lat, max_lon, max_lat = ll[0], ll[1], ur[0], ur[1]

        # Get (x, y) of the 4 cardinal points
        tl = (min_lon, max_lat)
        bl = (min_lon, min_lat)
        tr = (max_lon, max_lat)
        br = (max_lon, min_lat)

        return (tl, bl, tr, br) if cardinal else (min_lon, min_lat, max_lon, max_lat)
    
    def get_aoi_shp(self, dwnDir=''):
        """ 
        Create the .shp file corresponding to the selected aoi
        
        Args:
            dwnDir (str | pathlib.Path): the path to directory that will store the ESRI shapefiles
            
        Return:
            (str): the absolute path to the .shp file
        """
        
        aoi_name = self.get_aoi_name()
        
        if type(dwnDir) == str:
            dwnDir = Path(dwnDir).expanduser()
            
        filename = dwnDir.joinpath(f'{aoi_name}.shp')
    
        if filename.is_file():
            return filename
    
        # verify that the asset exist
        aoi = self.get_aoi_ee()
    
        # convert into json
        aoi_json = geemap.ee_to_geojson(aoi)
        
        # convert to geopandas gdf
        gdf = gpd.GeoDataFrame.from_features(aoi_json).set_crs('EPSG:4326')
        
        # FAO GAUL geometries are full of linestring which cannot be converted into shapefile so some filtering needs to be done first 
        gdf_filtered = gdf.copy()

        for i, row in gdf.iterrows():
            if type(row.geometry) == sg.collection.GeometryCollection:

                # get the polygon and only keep the polygon 
                for shape in row.geometry:
                    if type(shape) == sg.polygon.Polygon:
                        gdf_filtered.at[i, 'geometry'] = shape
                        break
        
        gdf_filtered.to_file(filename)
    
        return filename
    
    def get_aoi_name(self):
        """ 
        Get the aoi name based on the current state. 
        It will be an ISO 3166-1 alpha-3 if it's a country name and the asset stem for the rest. 
        Remove the `aoi_` string before the name of asset as it's a creation prefix convention.
        Return None if there is nothing. 
        
        Return:
            (str): the aoi name
        """
        
        name = None
        if self.country_code:
            name = self.country_code
        elif self.assetId:
            name = Path(self.assetId).stem.replace('aoi_', '')
        
        return name