#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os 
if 'GDAL_DATA' in list(os.environ.keys()): del os.environ['GDAL_DATA']

import collections

import geemap
import ee 
from haversine import haversine
import xarray_leaflet
import numpy as np
import rioxarray
import xarray as xr
import matplotlib.pyplot as plt
import ipywidgets as widgets
from ipyleaflet import WidgetControl, LocalTileLayer, TileLayer
import ipyvuetify as v

from sepal_ui.scripts import utils as su

#initialize earth engine
if not ee.data._credentials: ee.Initialize()


class SepalMap(geemap.Map):
    """initialize differents maps and tools"""

    def __init__(self, basemaps=[], dc=False, **kwargs):

        super().__init__(
            add_google_map=False, 
            center = [0,0],
            zoom = 2,
            **kwargs)
        
        # init the rasters
        self.loaded_rasters = {}
        
        # add the basemaps
        self.clear_layers()
        if len(basemaps):
            for basemap in set(basemaps):
                self.add_basemap(basemap)
        else:
            self.add_basemap('CartoDB.DarkMatter')
        
        # add the base controls
        self.clear_controls()
        self.add_control(geemap.ZoomControl(position='topright'))
        self.add_control(geemap.LayersControl(position='topright'))
        self.add_control(geemap.AttributionControl(position='bottomleft'))
        self.add_control(geemap.ScaleControl(position='bottomleft', imperial=False))
        
        # specific drawing control
        self.set_drawing_controls(dc)

        # Create output space for raster interaction
        self.output_r = widgets.Output(layout={'border': '1px solid black'})
        self.output_control_r = WidgetControl(widget=self.output_r, position='bottomright')
        self.add_control(self.output_control_r)

        # define interaction with rasters
        self.on_interaction(self.raster_interaction)
        
    def raster_interaction(self, **kwargs):
        """Define a behavior when ispector checked and map clicked"""
        
        if kwargs.get('type') == 'click' and self.inspector_checked:
            latlon = kwargs.get('coordinates')
            self.default_style = {'cursor': 'wait'}

            local_rasters = [lr.name for lr in self.layers if isinstance(lr, LocalTileLayer)]

            if local_rasters:

                with self.output_r: 
                    self.output_r.clear_output(wait=True)
                    
                    for lr_name in local_rasters:

                        lr = self.loaded_rasters[lr_name]
                        lat, lon = latlon

                        # Verify if the selected latlon is the image bounds
                        if any([lat<lr.bottom, lat>lr.top, lon<lr.left, lon>lr.right]):
                            print('Location out of raster bounds')
                        else:
                            # row in pixel coordinates
                            y = int(((lr.top - lat) / abs(lr.y_res)))

                            # column in pixel coordinates
                            x = int(((lon - lr.left) / abs(lr.x_res)))

                            # get height and width
                            h, w = lr.data.shape
                            value = lr.data[y][x]
                            print(f'{lr_name}')
                            print(f'Lat: {round(lat,4)}, Lon: {round(lon,4)}')
                            print(f'x:{x}, y:{y}')
                            print(f'Pixel value: {value}')
            else:
                with self.output_r:
                    self.output_r.clear_output()

            self.default_style = {'cursor': 'crosshair'}
            
            return

    def set_drawing_controls(self, bool_=False):
        """create a drawing control for the map"""
        
        color = v.theme.themes.dark.info
        
        dc = None
        if bool_:
            dc = geemap.DrawControl(
                marker       = {},
                circlemarker = {},
                polyline     = {},
                rectangle    = {'shapeOptions': {'color': color}},
                circle       = {'shapeOptions': {'color': color}},
                polygon      = {'shapeOptions': {'color': color}},
            )
            
        self.dc = dc
        
        return self

    def _remove_local_raster(self, local_layer):

        """ Remove local layer from memory"""
        name = local_layer if type(local_layer) == str else local_layer.name
        
        if name in self.loaded_rasters.keys():
            self.loaded_rasters.pop(name)
            
        return self

    def remove_last_layer(self, local=False):

        """Remove last layer from Map

        Args:
            local (boolean): Specify True to only remove local last layers,
                                otherwise will remove every last layer.

        """
        if len(self.layers) > 1:

            last_layer = self.layers[-1]

            if local:
                local_rasters = [lr for lr in self.layers if isinstance(lr, LocalTileLayer)]
                if local_rasters:
                    last_layer = local_rasters[-1]
                    self.remove_layer(last_layer)

                    # If last layer is local_layer, remove it from memory
                    if isinstance(last_layer, LocalTileLayer):
                        self._remove_local_raster(last_layer)
            else:
                self.remove_layer(last_layer)

                # If last layer is local_layer, remove it from memory
                if isinstance(last_layer, LocalTileLayer):
                    self._remove_local_raster(last_layer)
                    
        return self
              
    def zoom_ee_object(self, ee_geometry, zoom_out=1):
        
        #center the image
        self.centerObject(ee_geometry)
        
        #extract bounds from ee_object 
        ee_bounds = ee_geometry.bounds().coordinates()
        coords = ee_bounds.get(0).getInfo()
        ll, ur = coords[0], coords[2]

        # Get the bounding box
        min_lon, min_lat, max_lon, max_lat = ll[0], ll[1], ur[0], ur[1]


        # Get (x, y) of the 4 cardinal points
        tl = (max_lat, min_lon)
        bl = (min_lat, min_lon)
        tr = (max_lat, max_lon)
        br = (min_lat, max_lon)
        
        #zoom on these bounds 
        self.zoom_bounds([tl, bl, tr, br], zoom_out)
        
        return self 
    
    def zoom_bounds(self, bounds, zoom_out=1):
        """ 
        Get the proper zoom to the given bounds.

        Args:
            bounds (list of tuple(x,y)): coordinates of tl, bl, tr, br points
            zoom_out (int) (optional): Zoom out the bounding zoom
        """
        
        tl, bl, tr, br = bounds        
        
        maxsize = max(haversine(tl, br), haversine(bl, tr))
        
        lg = 40075 #number of displayed km at zoom 1
        zoom = 1
        while lg > maxsize:
            zoom += 1
            lg /= 2

        if zoom_out > zoom:
            zoom_out = zoom - 1

        self.zoom = zoom-zoom_out
        
        return self
    
    def update_map(self, assetId, bounds, remove_last=False):
        """Update the map with the asset overlay and removing the selected drawing controls
        
        Args:
            assetId (str): the asset ID in gee assets
            bounds (list of tuple(x,y)): coordinates of tl, bl, tr, br points
            remove_last (boolean) (optional): Remove the last layer (if there is one) before 
                                                updating the map
        """  
        if remove_last:
            self.remove_last_layer()

        self.zoom_bounds(bounds, zoom_out=2)
        self.centerObject(ee.FeatureCollection(assetId), zoom=self.zoom)
        self.addLayer(ee.FeatureCollection(assetId), {'color': 'green'}, name='aoi')
        
        return self
    
    #copy of the geemap add_raster function to prevent a bug from sepal 
    def add_raster(self, image, bands=None, layer_name='Layer_' + su.random_string(), colormap=plt.cm.inferno, x_dim='x', y_dim='y', opacity=1.0):
        """Adds a local raster dataset to the map.
        Args:
            image (str): The image file path.
            bands (int or list, optional): The image bands to use. It can be either a number (e.g., 1) or a list (e.g., [3, 2, 1]). Defaults to None.
            layer_name (str, optional): The layer name to use for the raster. Defaults to None.
            colormap (str, optional): The name of the colormap to use for the raster, such as 'gray' and 'terrain'. More can be found at https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html. Defaults to None.
            x_dim (str, optional): The x dimension. Defaults to 'x'.
            y_dim (str, optional): The y dimension. Defaults to 'y'.
        """
        if not os.path.exists(image):
            return print('The image file does not exist.')
            

        # check inputs
        if layer_name in self.loaded_rasters.keys():
            layer_name = layer_name+su.random_string()

        if isinstance(colormap, str):
            colormap = plt.cm.get_cmap(name=colormap)

        da = rioxarray.open_rasterio(image, masked=True)

        # Create a named tuple with raster bounds and resolution
        local_raster = collections.namedtuple(
            'LocalRaster', ('name', 'left', 'bottom', 'right', 'top', 'x_res', 'y_res', 'data')
            )(layer_name, *da.rio.bounds(), *da.rio.resolution(), da.data[0])

        self.loaded_rasters[layer_name] = local_raster


        multi_band = False
        if len(da.band) > 1:
            multi_band = True
            if not bands:
                bands = [3, 2, 1]
        else:
            bands = 1

        if multi_band:
            da = da.rio.write_nodata(0)
        else:
            da = da.rio.write_nodata(np.nan)
        da = da.sel(band=bands)

        if multi_band:
            layer = da.leaflet.plot(self, x_dim=x_dim, y_dim=y_dim, rgb_dim='band')
        else:
            layer = da.leaflet.plot(self, x_dim=x_dim, y_dim=y_dim, colormap=colormap)

        layer.name = layer_name

        
        layer.opacity = opacity if abs(opacity) <= 1.0 else 1.0
        
        return
    
    def show_dc(self):
        """add the drawing control on the map"""
        
        if self.dc:
            self.dc.clear()
        
            if not self.dc in self.controls:
                self.add_control(self.dc)
            
        return self
    
    def hide_dc(self):
        """remove the drawing control from the map"""
        
        if self.dc:
            self.dc.clear()
        
            if self.dc in self.controls:
                self.remove_control(self.dc)
                
        return self
        
        
        
