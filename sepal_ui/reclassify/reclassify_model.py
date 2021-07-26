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
    
    def reclassify(self):
        """
        Reclassify the input according to the provided matrix. For vector file type reclassifying correspond to add an extra column at the end
        """
        
        @su.need_ee
        def _ee_image(self, matrix):
            
            # create the asset description 
            self.dst_ee = f'{Path(self.ee_local).stem}_reclass'
            
            # load the image
            # remap according to the matrix
            from_ = [v for v in matrix.keys()]
            to_ = [v for v in matrix.values()]
            
            ee_image = ee.Image(self.src_ee).remap(from_, to_, 0, self.band)
            
            # export 
            params = {
                'image': ee_image,
                'assetId': self.dst_ee,
                'description': self.dst_ee,
                'scale': 30, # it should be the native resolution of the original image
                'maxPixels': 1e13,
            }

            task = ee.batch.Export.image.toAsset(**params)
            task.start()
        
            return

        @su.need_ee
        def _ee_vector(self):
            
            # create the asset description 
            self.dst_ee = f'{Path(self.ee_local).stem}_reclass'
            
            # add a new propertie
            def add_prop(feat):
                props = feat.getInfo()['properties']
                new_val = feat.get(self.band)
                return ee.Feature(new_val).copyProperties(feat, keepProperties)
            
            ee_fc = ee.FeatureCollection(self.src_ee).map(add_prop)
            
            # export 
            params = {
                'collection': ee_fc,
                'assetId': self.dst_ee,
                'description': self.dst_ee,
            }

            task = ee.batch.Export.table.toAsset(**params)
            task.start()
            
            return
        
        def _local_image(self, matrix):
            
            # set the output file 
            self.dst_local = self.dst_dir/f'{Path(self.src_local).stem}_reclass.tif'
                        
            with rio.open(self.src_local) as src_f, rio.open(self.dst_local) as dst_f: 
                
                profile = f.profile
                profile.update(driver='GTiff', count=1, compress='lzw', dtype=np.uint8)
                
                # workon each window to avoid memory problems
                windows = [w for _, w in src.block_windows()]
                for window in windows:
                    
                    # read the window 
                    raw = f.read(self.band, window=window).astype(np.uint8)
                    
                    # reclassify the image based on the matrix 
                    # every value that is not specified will be set to 0 
                    data = np.zeros_like(raw)
                    
                    for old_val, new_val  in matrix.items():
                        data += (raw == old_val) * new_val 
                    
                    # write it in the destination file
                    dst.write(data, 1, window=window)
            
            return

        def _local_vector(self):

            # set the output file 
            self.dst_local = self.dst_dir/f'{Path(self.src_local).stem}_reclass.shp'
            
            # read the dataset
            gdf = gpd.read_file(self.src_local)
            
            # map the new column 
            gdf['reclass'] = gdf.apply(lambda row: matrix[row[self.band]])
            
            # save the file 
            gdf.to_file(self.dst_local)
            
            return
            
        # map all the function in the guess matrix (gee, type) 
        reclassify_func = [[_local_vector, _local_image],[_ee_vector, _ee_image]]
        
        # reshape the matrix so that every value correspond to 1 key
        matrix = {}
        for new_val, list_ in self.matrix:
            for old_val in list_:
                matrix[old_val] = new_val
        
        # return the selected function 
        # remember to use self as a parameter
        return reclassify_func[self.gee][self.input_type](self, matrix) 
        
