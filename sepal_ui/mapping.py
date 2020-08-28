#!/usr/bin/env python3

import geemap
import ee 
from haversine import haversine

#initialize earth engine
ee.Initialize()


class SepalMap(geemap.Map):
    """initialize differents maps and tools"""

    def __init__(self, basemaps=None, dc=False, **kwargs):

        super().__init__(
            add_google_map=False, 
            center = [0,0],
            zoom = 2,
            **kwargs)
        
        #add the basemaps
        self.clear_layers()
        if len(basemaps):
            for basemap in basemaps:
                self.add_basemap(basemap)
        else:
            self.add_basemap('CartoDB.DarkMatter')
        
        #add the base controls
        self.clear_controls()    
        self.add_control(geemap.ZoomControl(position='topright'))
        self.add_control(geemap.LayersControl(position='topright'))
        self.add_control(geemap.AttributionControl(position='bottomleft'))
        self.add_control(geemap.ScaleControl(position='bottomleft', imperial=False))
        
        #specific drawing control
        self.set_drawing_controls(dc)

    def set_drawing_controls(self, bool_=True):
        if bool_:
            dc = geemap.DrawControl(
                marker={},
                circlemarker={},
                polyline={},
                rectangle={'shapeOptions': {'color': '#0000FF'}},
                circle={'shapeOptions': {'color': '#0000FF'}},
                polygon={'shapeOptions': {'color': '#0000FF'}},
            )
        else:
            dc = None
            
        self.dc = dc
        
        return self
        
    def remove_last_layer(self):
        
        if len(self.layers) > 1:
            last_layer = self.layers[-1]
            self.remove_layer(last_layer)
            
            
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

        self.set_zoom(bounds, zoom_out=2)
        self.centerObject(ee.FeatureCollection(assetId), zoom=self.zoom)
        self.addLayer(ee.FeatureCollection(assetId), {'color': 'green'}, name='aoi')