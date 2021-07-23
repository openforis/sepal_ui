import warnings
from pathlib import Path

from pandas import DataFrame
import numpy as np
import rasterio as rio

from traitlets import Unicode, Any, Dict, List, Bool

from sepal_ui.model import Model
from sepal_ui.scripts import gee


import ee
ee.Initialize()

class ReclassifyModel(Model):
    
    in_raster = Any(None).tag(sync=True) # should be unicode but we need to handle when nothing is set (None)
    dst_raster = Any(None).tag(sync=True) # should be unicode but we need to handle when nothing is set (None)
    band = Any(None).tag(sync=True)
    
    asset_id = Any(None).tag(sync=True) # should be unicode but we need to handle when nothing is set (None)
    code_col = Any('').tag(sync=True)
    
    matrix = Dict({}).tag(sync=True)

    classes_files = List([]).tag(sync=True)
    
    # Create a state var, to determine if an asset has been remaped
    remaped = Bool(False).tag(sync=True)
    
    def __init__(self, gee=False, results_dir=None, **kwargs):
        
        super().__init__(**kwargs)
        
        self.results_dir = results_dir
        
        # save relation with gee 
        self.gee = gee
        
        self.asset_type = None
        self.ee_object = None
        
        # Memory assets
        self.raster_reclass = None
        self.out_profile = None
        self.reclass_ee = None
        
    def get_bands(self):
        """get the band number for raster/asset"""
        
        if self.gee:
            bands = ee.Image(self.asset_id).bandnames().getInfo()
        else:
            with rio.open(self.in_raster) as f:
                bands = [i for i in range(1,f.count+1)]
        
        return bands
    
    def unique(self):
        """Retreive all the existing feature in the file according to the file type"""
        
        if self.gee:
            pass
        else:
            
            raster = Path(self.in_raster)
            
            if not raster.is_file():
                raise Exception('There is not any raster file selected')
            
            with rio.open(raster) as src:
                
                count = np.bincount(src.read(1).flatten())
                features = np.nonzero(count!=0)[0].tolist()
            
            return features
    
    def get_unique_ee(self, maxBuckets=40000):
        """Get unique values (or classes) from a categorical EE image"""
        
        if not self.code_col:
            raise Exception("Please select a band")
        
        # Reduce image
        reduced = self.ee_object.reduceRegion(
          reducer = ee.Reducer.autoHistogram(maxBuckets=maxBuckets), 
          geometry = self.ee_object.geometry(), 
          scale=30, 
          maxPixels=1e13
        )

        array = ee.Array(ee.List(reduced.get(self.code_col))).getInfo()
        
        if len(array) > 256:
            raise Exception("Too many values to reclassify. Are you trying " + \
            "to reclassify a coded Asset?")
                            
        df = DataFrame(data=array, columns=['code', 'count'])
        
        return list(df[df['count']>0]['code'].unique())
        

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
            
    def validate_asset(self):
        
        asset = self.asset_id
        
        asset_info = ee.data.getAsset(asset)
        self.asset_type = asset_info['type']
        
        if self.asset_type == 'TABLE':
            self.ee_object = ee.FeatureCollection(asset)
            
        elif self.asset_type == 'IMAGE':
            self.ee_object = ee.Image(asset)
        
        else:
            raise AttributeError("cm.remap.error_type")
            
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
        
