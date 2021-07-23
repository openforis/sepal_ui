import warnings
from pathlib import Path

import pandas as pd
import geopandas as gpd
import numpy as np
import rasterio as rio

from traitlets import Unicode, Any, Dict, List, Bool

from sepal_ui.model import Model
from sepal_ui.scripts import gee
from sepal_ui.scripts import utils as su


import ee
ee.Initialize()

class ReclassifyModel(Model):
    
    # should be unicode but we need to handle when nothing is set (None)
    
    # parameters of the model linked to widgets
    band = Any(None).tag(sync=True)
    src_local = Any(None).tag(sync=True)
    src_gee = Any(None).tag(sync=True)
    dst_class_file = Any(None).tag(sync=True)
    
    # data manipulation
    matrix = Dict({}).tag(sync=True)
    
    # Create a state var, to determine if an asset has been remaped
    remaped = Bool(False).tag(sync=True)
    
    def __init__(self, gee=False, dst_dir=None, **kwargs):
        
        # init the model
        super().__init__(**kwargs)
        
        # save the folder where the results should be stored
        # only used for local export
        self.dst_dir = Path(dst_dir) if dst_dir else Path.home()
        
        # save relation with gee 
        self.gee = gee
        
        # init output to None 
        self.input_type = None # 1 raster, 0 vector
        self.src_class = None
        self.dst_class = None
        self.dst_local = None
        self.dst_gee = None
        
    def get_dst_classes(self):
        """extract the classes from the class file"""
        
        df = pd.read_csv(self.dst_class_file, header=None)
        
        # dst_class_file should be set on the model csv output of the custom view 
        # 3 column: 1: code, 2: name, 3: color 
        
        # guess if there is a header
        if all(df.iloc[0].apply(lambda x: isinstance(x, str))):
            df = df[1:].reset_index(drop=True)
        
        df = df.rename(columns={0: 'code', 1: 'desc'})#, 2: 'color'})
        
        # save the df for reclassify useage
        self.dst_class = df
        
        # create a dict out of it 
        return {row.code: row.desc for i, row in df.iterrows()}
    
    def get_type(self):
        """
        Guess the type of the input and set the input type attribute for the model
        """
        
        if self.gee: 
            if not self.src_gee: raise Exception ('no input')
                
            asset_info = ee.data.getAsset(self.src_gee)['type']
        
            if asset_info == 'TABLE':
                self.input_type = False
            elif asset_info == 'IMAGE':
                self.input_type = True
            else:
                raise AttributeError("wrong type")
                
        else:
            if not self.src_local: raise Exception ('no input')
            
            input_path = Path(self.src_local)
            
            if input_path.suffix in ['.geojson', '.shp']:
                self.input_type = False
            elif input_path.suffix in ['.tif', '.tiff', '.vrt']:
                self.input_type = True
            else:
                raise AttributeError("wrong type")
                
        return self
    
    def get_bands(self):
        """
        based on the input type and use the appropriate band request 
        get the available bands/feature from the input
        """
    
        @su.need_ee
        def _ee_image(self):

            return sorted(ee.Image(self.src_gee).bandNames().getInfo())

        @su.need_ee
        def _ee_vector(self):

            columns = ee.FeatureCollection(self.src_gee).first().getInfo()['properties']

            return sorted(str(c) for c in columns.keys() if c not in ['system:index', 'Shape_Area'])

        def _local_image(self):

            with rio.open(self.src_local) as f:
                bands = [i for i in range(1,f.count+1)]

            return sorted(bands)

        def _local_vector(self):

            df = gpd.read_file(self.src_local)

            return [c for c in df.columns.tolist() if c != 'geometry']
        
        # map all the function in the guess matrix (gee, type) 
        band_func = [[_local_vector, _local_image],[_ee_vector, _ee_image]]
        
        # return the selected function 
        # remember to use self as a parameter
        return band_func[self.gee][self.input_type](self)
    
    def unique(self):
        """
        Retreive all the existing feature in the input according to the model parameters
        """
        
        @su.need_ee
        def _ee_image(self):
            
            # reduce the image
            image = ee.Image(self.src_gee).select(self.band)
            reduction = image.reduceRegion(ee.Reducer.frequencyHistogram(), image.geometry())
            
            # Remove all the unnecessary reducer output structure and make a list of values.
            values = ee.Dictionary(reduction.get(image.bandNames().get(0))) \
                .keys() \
                .getInfo()
            
            return [int(v) for v in values]

        @su.need_ee
        def _ee_vector(self):
            
            # get the feature
            values = ee.FeatureCollection(self.src_gee).aggregate_array(self.band).getInfo()
            
            return list(set(values))

        def _local_image(self):

            with rio.open(self.src_local) as src:
                
                count = np.bincount(src.read(self.band).flatten())
                features = np.nonzero(count!=0)[0].tolist()

            return features

        def _local_vector(self):
            """get the band list from ee image"""

            df = gpd.read_file(self.src_local)

            return df[self.band].unique().tolist()
        
        # map all the function in the guess matrix (gee, type) 
        unique_func = [[_local_vector, _local_image],[_ee_vector, _ee_image]]
        
        # return the selected function 
        # remember to use self as a parameter
        return unique_func[self.gee][self.input_type](self)        

    def reclassify_raster(self, 
                          map_values, 
                          dst_raster=None, 
                          overwrite=False, 
                          save=True):
        
        """ 
        Remap raster values from a map_values dictionary. If the 
        are missing values in the dictionary 0 value will be returned

        Args:
            map_values (dict): Dictionary with origin:target values
            
        """
        if not Path(self.in_raster).is_file():
            raise Exception('There is not any raster file selected')
            
            
        # Get reclassify path raster
        filename = Path(self.in_raster).stem

        if not dst_raster:
            dst_raster = Path(self.results_dir)/f'{filename}_reclassified.tif'

        if not overwrite:
            if dst_raster.is_file():
                raise Warning(cm.bin.reclassify_exist.format(dst_raster))
            else:
                raise Exception(cm.bin.no_exists.format(dst_raster))

        change_matrix = self.validate_map_values(map_values)

        with rio.open(self.in_raster) as src:

            raw_data = src.read()
            self.out_profile = src.profile
            self.out_profile.update(compress='lzw', dtype=np.uint8)
            
            data = np.zeros_like(raw_data, dtype=np.uint8)
            
            for origin, target in change_matrix:

                bool_data = np.zeros_like(raw_data, dtype=np.bool_)
                bool_data = bool_data + (raw_data == origin)

                data_value = (bool_data * target).astype(np.uint8)

                data += data_value
            
            self.raster_reclass = data
            
            if save:
                with rio.open(dst_raster, 'w', **self.out_profile) as dst:
                    dst.write(self.raster_reclass)
                    
        self.remaped=True
    
    def validate_map_values(self, map_values):
        
        values = list(map_values.values())
        
        if not all(values):
            raise Exception('All new values must be filled, try it again.')

        matrix = {
            int(k): int(v['value']) if isinstance(v, dict) else int(v)
                for k, v in map_values.items()
        }
        
        return matrix
    
    def remap_ee_object(self, band, change_matrix, save=False):
        """Get input with new remaped classes, it can process feature collection
        or images

        Args:
            ee_object (ee.Image, ee.FeatureCollection)
            band (str): Name of band where are the values, if feature collection
                        is selected, column name has to be filled.
            matrix (Remap.matrix dictionary): dictionary with {from:to values}
        """
        
        change_matrix = self.validate_map_values(change_matrix)
        
        # Get from, to lists
        origin, target = list(zip(*change_matrix.items()))
        
        
        if self.asset_type == 'IMAGE':
            # Remap image
            self.reclass_ee = self.ee_object.remap(
                origin, target, bandName=band).rename([band])
        else:
            # Remap table
            self.reclass_ee = self.ee_object.remap(
                origin, target, columnName=band)
            
        
        if save:
            name = Path(self.ee_object.getInfo()['id']).stem
            return self.export_ee_image(name)
        
        # is the asset already remapped?
        self.remaped=True

            
    def export_ee_image(self, name, folder=None):
        
        def create_name(name):

            if name[-1].isdigit():
                last_number = int(name[-1])
                name = name[:-1] + f'{last_number+1}'
            else:
                name += '_1'

            return name
        
        asset_name = name+'_reclass'
        folder = folder if folder else ee.data.getAssetRoots()[0]['id']
        
        asset_id = str(Path(folder, asset_name))
        
        # check if the table already exist
        current_assets = [a['name'] for a in gee.get_assets(folder)]
        
        # An user could reclassify twice an asset,
        # So let's create an unique name
        while (asset_id in current_assets):
            asset_id = create_name(asset_id)

        params = {
            'image': self.reclass_ee,
            'assetId': asset_id,
            'description': Path(asset_id).stem,
            'scale': 30,
            'maxPixels': 1e13,
        }

        task = ee.batch.Export.image.toAsset(**params)
        task.start()

        return task.id, asset_id        
        
            
    def get_fields(self, ee_object=None, code_col=None):
        """Get fields from Feature Collection"""
        
        ee_object = self.ee_object if not ee_object else ee_object
        code_col = self.code_col if not code_col else code_col
        
        if not self.code_col:
            raise Exception("Please provide a column")
        
        return sorted(
            list(set(
                ee_object.aggregate_array(code_col).getInfo()
            ))
        ) 

    def get_cols(self, only_int=True):
        """Get columns from featurecollection asset"""

        columns = self.ee_object.first().getInfo()['properties']
        
        if only_int:
            columns = [col for col, val in columns.items() if type(val) in [int, float]]
        else:
            columns = list(columns.keys())
            

        return sorted(
            [
                str(col) for col 
                in columns if col not in ['system:index', 'Shape_Area']
            ])
    
    #def get_bands(self):
    #    """Get bands from Image asset"""
    #    
    #    if not self.ee_object:
    #        raise Exception('To get bands of an asset you must select one')
    #        
    #    return list(self.ee_object.bandTypes().getInfo().keys())
        
