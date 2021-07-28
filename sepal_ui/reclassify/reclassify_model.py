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
from matplotlib.colors import to_rgba


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
        df = df.rename(columns={0: 'code', 1: 'desc', 2: 'color'})
        
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
        Reclassify the input according to the provided matrix. For vector file type reclassifying correspond to add an extra column at the end. vizualization colors will be set.
        """
        
        @su.need_ee
        def _ee_image(self, matrix):
            
            # create the asset description 
            self.dst_gee = Path(self.src_gee).with_name(f'{Path(self.src_gee).stem}_reclass')
            
            # load the image
            # remap according to the matrix
            from_ = [v for v in matrix.keys()]
            to_ = [v for v in matrix.values()]
            
            ee_image = ee.Image(self.src_gee) \
                .remap(from_, to_, 0, self.band) \
                .select(['remapped'], [self.band])
            
            # gather all the other band in the image 
            ee_image = ee.Image(self.src_gee).addBands(ee_image, overwrite=True)
            
            # add colormapping parameters
            # set return an element so we force cast it to ee.Image
            desc = [str(e) for e in self.dst_class.desc.tolist()]
            color = [str(e) for e in self.dst_class.color.tolist()]
            code = [str(e) for e in self.dst_class.code.tolist()]
            
            ee_image = ee.Image(ee_image.set({
                'visualization_0_name': 'Classification',
                'visualization_0_bands': self.band,
                'visualization_0_type': 'categorical',
                'visualization_0_labels': ','.join(desc),
                'visualization_0_palette': ','.join(color),
                'visualization_0_values': ','.join(code)   
            }))
            
            # export 
            params = {
                'image': ee_image,
                'assetId': str(self.dst_gee),
                'description': self.dst_gee.stem,
                'scale': 30, # it should be the native resolution of the original image
                'maxPixels': 1e13,
            }

            task = ee.batch.Export.image.toAsset(**params)
            task.start()
        
            return

        @su.need_ee
        def _ee_vector(self):
            
            # create the asset description 
            self.dst_ee = f'{Path(self.src_gee).stem}_reclass'
            
            # add a new propertie
            def add_prop(feat):
                props = feat.getInfo()['properties']
                new_val = feat.get(self.band)
                return ee.Feature(new_val).copyProperties(feat, keepProperties)
            
            ee_fc = ee.FeatureCollection(self.src_gee).map(add_prop)
            
            # add colormapping parameters
            
            # export 
            params = {
                'collection': ee_fc,
                'assetId': self.dst_gee,
                'description': self.dst_gee,
            }

            task = ee.batch.Export.table.toAsset(**params)
            task.start()
            
            return
        
        def _local_image(self, matrix):
            
            # set the output file 
            self.dst_local = self.dst_dir/f'{Path(self.src_local).stem}_reclass.tif'
                        
            with rio.open(self.src_local) as src_f: 
                
                profile = src_f.profile
                profile.update(driver='GTiff', count=1, compress='lzw', dtype=np.uint8)
                
                with rio.open(self.dst_local, 'w', **profile) as dst_f:
                
                    # workon each window to avoid memory problems
                    windows = [w for _, w in src_f.block_windows()]
                    for window in windows:

                        # read the window 
                        raw = src_f.read(self.band, window=window)

                        # reclassify the image based on the matrix 
                        # every value that is not specified will be set to 0 
                        data = np.zeros_like(raw, dtype=np.int64)

                        for old_val, new_val  in matrix.items():
                            data += (raw == old_val) * new_val 

                        # write it in the destination file
                        dst_f.write(data.astype(np.uint8), 1, window=window)

                    # add the colors to the image
                    colormap = {}
                    for i, row in self.dst_class.iterrows():
                        print(row.color)
                        print(to_rgba(row.color))
                        print(type(to_rgba(row.color)))
                        colormap[row.code] = tuple(int(c*255) for c in to_rgba(row.color))

                    dst_f.write_colormap(self.band, colormap)
            
            return

        def _local_vector(self):

            # set the output file 
            self.dst_local = self.dst_dir/f'{Path(self.src_local).stem}_reclass.shp'
            
            # read the dataset
            gdf = gpd.read_file(self.src_local)
            
            # map the new column 
            gdf['reclass'] = gdf.apply(lambda row: matrix[row[self.band]])
            
            # add the colors to the gdf 
            # waiting for an answer there : https://gis.stackexchange.com/questions/404946/how-can-i-save-my-geopandas-symbology
        
            # save the file 
            gdf.to_file(self.dst_local)
            
            return
            
        # map all the function in the guess matrix (gee, type) 
        reclassify_func = [[_local_vector, _local_image],[_ee_vector, _ee_image]]
        
        # reshape the matrix so that every value correspond to 1 key
        matrix = {}
        for new_val, list_ in self.matrix.items():
            for old_val in list_:
                matrix[old_val] = new_val
        
        # return the selected function 
        # remember to use self as a parameter
        return reclassify_func[self.gee][self.input_type](self, matrix) 
        
