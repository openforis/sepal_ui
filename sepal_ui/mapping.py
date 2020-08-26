#!/usr/bin/env python3

import geemap
from ipyleaflet import basemap_to_tiles, ZoomControl, LayersControl, AttributionControl, ScaleControl, DrawControl
import ee 
from haversine import haversine

#initialize earth engine
ee.Initialize()


class SepalMap(geemap.Map):

    def __init__(self, **kwargs):

        """  Initialize Sepal Map.

        Args:

            basemap (str): Select one of the Sepal Base Maps available.


        """

        basemap = dict(
            url='http://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
            max_zoom=20,
            attribution='&copy; <a href="http://www.openstreetmap.org/copyright">\
            OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">\
            CartoDB</a>',
            name='CartoDB.DarkMatter'
        )

        basemap = basemap_to_tiles(basemap)

        super().__init__(**kwargs, add_google_map=False, basemap=basemap)
        
        self.center = [0,0]
        self.zoom = 2
        
        super().clear_controls()
        
        self.add_control(ZoomControl(position='topright'))
        self.add_control(LayersControl(position='topright'))
        self.add_control(AttributionControl(position='bottomleft'))
        self.add_control(ScaleControl(position='bottomleft', imperial=False))

    def get_drawing_controls(self):

        dc = DrawControl(
            marker={},
            circlemarker={},
            polyline={},
            rectangle={'shapeOptions': {'color': '#0000FF'}},
            circle={'shapeOptions': {'color': '#0000FF'}},
            polygon={'shapeOptions': {'color': '#0000FF'}},
         )

        return dc
        
    def remove_last_layer(self):
        
        if len(self.layers) > 1:
            last_layer = self.layers[-1]
            self.remove_layer(last_layer)

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

        self.set_zoom(bounds, zoom_out=2)
        self.centerObject(ee.FeatureCollection(assetId), zoom=self.zoom)
        self.addLayer(ee.FeatureCollection(assetId), {'color': 'green'}, name='aoi')


    def set_zoom(self, bounds, zoom_out=1):
        """ Get the proper zoom to the given bounds.

        Args:

            bounds (list of tuple(x,y)): coordinates of tl, bl, tr, br points
            zoom_out (int) (optional): Zoom out the bounding zoom

        Returns:

            zoom (int): Zoom for the given ee_asset
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
