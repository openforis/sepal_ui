from pathlib import Path

import numpy as np
import rasterio as rio

from traitlets import Unicode, Any

from sepal_ui.model import Model

import ee
ee.Initialize()

class ReclassifyModel(Model):
    
    in_raster = Unicode('').tag(sync=True)
    dst_raster = Unicode('').tag(sync=True)
    
    asset_id = Unicode('').tag(sync=True)
    ee_code_Col = Any('').tag(sync=True)
    
    def __ini__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.asset_type = None
        self.ee_object = None
    
    def unique(self):
        """Retreive all the existing feature in the byte file"""
        
        if not Path(self.in_raster).is_file():
            raise Exception('There is not any raster file selected')

        features = []

        raster = Path(self.in_raster)

        with rio.open(raster) as src:

            data = src.read(1)
            count = np.bincount(data.flatten())
            del data

            features = np.where(count!=0)[0]
            features = features.tolist()

        return features

    def reclassify_from_map(self, map_values, dst_raster=None, overwrite=False):
        """ Remap raster values from map_values dictionary. If the 
        are missing values in the dictionary 0 value will be returned

        Args:
            in_raster (path to raster): Input raster to reclassify
            map_values (dict): Dictionary with origin:target values
        """
        if not Path(self.in_raster).is_file():
            raise Exception('There is not any raster file selected')
            
        # Get reclassify path raster
        filename = Path(self.in_raster).stem

        if not dst_raster:
            dst_raster = Path('~').expanduser()/f'downloads/{filename}_reclassified.tif'

        if not overwrite:
            if dst_raster.is_file():
                raise Warning(cm.bin.reclassify_exist.format(dst_raster))
            else:
                raise Exception(cm.bin.no_exists.format(dst_raster))

        if not all(list(map_values.values())):
            raise Exception('All new values has to be filled, try it again.')

        # Cast to integer map_values

        map_values = {k: int(v) for k, v in map_values.items()}

        with rio.open(self.in_raster) as src:

            raw_data = src.read()
            profile = src.profile
            profile.update(compress='lzw', dtype=np.uint8)

            data = np.zeros_like(raw_data, dtype=np.uint8)

            for origin, target in map_values.items():

                bool_data = np.zeros_like(raw_data, dtype=np.bool_)
                bool_data = bool_data + (raw_data == origin)

                data_value = (bool_data * target).astype(np.uint8)

                data += data_value

                with rio.open(dst_raster, 'w', **profile) as dst:
                    dst.write(data)

        return data
    
    def remap_feature_collection(self, band, matrix):
        """Get image with new remaped classes, it can process feature collection
        or images

        Args:
            ee_asset (ee.Image, ee.FeatureCollection)
            band (str): Name of band where are the values, if feature collection
                        is selected, column name has to be filled.
            matrix (Remap.matrix dictionary): dictionary with {from:to values}
        """

        # Get from, to lists
        from_, to = list(zip(*[(k, v['value']) for k, v in matrix.items()]))

        asset_type = ee.data.getAsset(ee_asset)

        if asset_type == 'TABLE':
            # Convert feature collection to raster
            image = ee_asset.filter(ee.Filter.notNull([band])).reduceToImage(
                properties=band, 
                reducer=ee.Reducer.first()).rename([band])

        elif asset_type == 'IMAGE':
            image = ee.asset
        # Remap image
        image.remap(from_, to, bandName=band)

        return image
    
    def validate_asset(self):
        
        asset = self.asset_id
        
        asset_info = ee.data.getAsset(asset)
        self.asset_type = asset_info['type']
        
        if self.asset_type == 'TABLE':
            self.ee_object = ee.FeatureCollection(asset)
            
        elif self.asset_type == 'IMAGE':
            self.ee_object = ee.Image(asset)
        
        else:
            raise AttributeError(cm.remap.error_type)
            
    def _get_fields(self):
        """Get fields from Feature Collection"""
        return sorted(
            list(set(
                self.ee_asset.aggregate_array(self.code_col).getInfo()
            ))
        ) 

    def get_cols(self):
        """Get columns from featurecollection asset"""

        columns = ee.Feature(
            self.ee_object.first()).propertyNames().getInfo()
        
        return sorted(
            [
                str(col) for col 
                in columns if col not in ['system:index', 'Shape_Area']
            ])
    
    def get_bands(self):
        """Get bands from Image asset"""
        
        if not self.ee_object:
            raise Exception('To get bands of an asset you must select one')
            
        return list(self.ee_object.bandTypes().getInfo().keys())
        
    def _get_classes(self, maxBuckets=40000):
        """Get raster classes"""
        
        # Reduce image
        reduced = self.ee_object.reduceRegion(
          reducer = ee.Reducer.autoHistogram(maxBuckets=maxBuckets), 
          geometry = self.ee_object.geometry(), 
          scale=30, 
          maxPixels=1e13
        )

        array = ee.Array(ee.List(reduced.get(self.code_col))).getInfo()
        df = DataFrame(data=array, columns=['code', 'count'])
        
        return list(df[df['count']>0]['code'].unique())