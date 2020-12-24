from pathlib import Path
import os

import ee
import geemap
import shapely.geometry as sg
import geopandas as gpd
import ipyvuetify as v 

from sepal_ui.scripts import utils as su
    
# initialize earth engine
su.init_ee()

class Aoi_io:
    
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
        self.feature_collection = None # to access the country

        #set up your inputs
        self.file_input = None
        self.file_name = None
        self.country_selection = None
        self.selection_method = None
        self.drawn_feat = None
        self.alert = alert_widget
        
    def get_aoi_ee(self):

        """ Returns an ee.asset from self, None if no aoi set"""
        
        obj = None
        if self.feature_collection:
            obj = self.feature_collection
        elif self.assetId:
            obj = ee.FeatureCollection(self.assetId)
            
        return obj
    
    def get_columns(self):

        """ Retrieve the columns or variables from self

        return: sorted list cof column names
        """
        
        aoi_ee = self.get_aoi_ee()
        columns = ee.Feature(aoi_ee.first()).propertyNames().getInfo()
        columns = sorted([col for col in columns if col not in ['system:index', 'Shape_Area']])
        
        return columns
    
    def get_fields(self, column=None):
        """" Retrieve the fields from the selected self column
        
        Args:
            column (str) (optional): Used to query over the asset
        
        return: sorted list of fields

        """
        
        if not column:
            column = self.column

        aoi_ee = self.get_aoi_ee()
        fields = sorted(aoi_ee.distinct(column).aggregate_array(column).getInfo())

        return fields

    def get_selected_feature(self):
        """ Select a ee object based on the current state.

        Returns:
            ee.geometry
        """

        if not self.column or not self.field:
            raise Exception('You must first select a column and a field.')

        ee_asset = self.get_aoi_ee()
        select_feature = ee_asset.filterMetadata(self.column, 'equals', self.field).geometry()

        # Specify the selected feature
        self.selected_feature = select_feature

        return select_feature

    def clear_selected(self):
        self.selected_feature = None

    def clear_attributes(self):

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

    def get_not_null_attrs(self):
        
        attrs = dict((k, v) for k, v in self.__dict__.items() if v is not None)
        
        return attrs

    def display_on_map(self, map_):
        """ Display the current aoi on a map and remove the dc

        Args:
            map_ (SepalMap): Map to display the element
        """
        aoi = self.get_aoi_ee()
        map_.zoom_ee_object(aoi.geometry())
        map_.addLayer(aoi, {'color': v.theme.themes.dark.success}, name='aoi')
        
        map_.hide_dc()
        
        return self


    def get_bounds(self, ee_object, cardinal=False):
        """ Returns the min(lon,lat) and max(lon, lat) from the given asset

        Args:
            ee_asset (ee.object): GEE asset (FeatureCollection, Geometry or str)
            cardinal (boolean) (optional)

        Returns:
            If cardinal True: returns cardinal points tl, bl, tr, br
            If cardinal False: returns bounding box
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
        """ create the .shp file corresponding to the selected aoi"""
        
        aoi_name = self.get_aoi_name()
            
        filename = os.path.join(dwnDir, f'{aoi_name}.shp')
    
        if os.path.isfile(filename):
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
        """ remove the aoi_ before the nam of the created asset"""
        
        name = None
        if self.country_code:
            name = self.country_code
        elif self.assetId:
            name = Path(self.assetId).stem.replace('aoi_', '')
        
        return name