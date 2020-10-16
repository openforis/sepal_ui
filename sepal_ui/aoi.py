#!/usr/bin/env python3
from functools import partial
from datetime import datetime
from pathlib import Path
import os

import ee
import ipyvuetify as v
import geemap
import shapely.geometry as sg
from osgeo import osr, ogr

from .mapping import SepalMap
from . import sepalwidgets as sw
from . import widgetBinding as wb
from .scripts import run_aoi_selection
from .scripts import messages as ms
from .scripts import utils as su

ee.Initialize()



class Aoi_io:
    
    def __init__(self, alert_widget=None, default_asset=None):
        """Initiate the Aoi object.

        Args:
            alert_widget (SepalAlert): Widget to display alerts.

        """

        # GEE parameters
        self.assetId = default_asset
        self.column = None
        self.field = None
        self.selected_feature = None

        #set up your inputs
        self.file_input = None
        self.file_name = 'Manual_{0}'.format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        self.country_selection = None
        self.selection_method = None
        self.drawn_feat = None
        self.alert = alert_widget
        
    def get_aoi_ee(self):

        """ Returns an ee.asset from self

        return: ee.Object

        """
        return ee.FeatureCollection(self.assetId)
    
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
            self.alert.add_msg('error', f'You must first select a column and a field.')
            raise 

        ee_asset = self.get_aoi_ee()
        select_feature = ee_asset.filterMetadata(self.column, 'equals', self.field).geometry()

        # Specify the selected feature
        self.selected_feature = select_feature

        return select_feature

    def clear_selected(self):
        self.selected_feature = None

    def clear_attributes(self):

        # GEE parameters
        self.column = None
        self.field = None
        self.selected_feature = None

        #set up your inputs
        self.file_input = None
        self.file_name = 'Manual_{0}'.format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        self.country_selection = None
        self.selection_method = None
        self.drawn_feat = None

    def get_not_null_attrs(self):
        return dict((k, v) for k, v in self.__dict__.items() if v is not None)

    def display_on_map(self, map_):
        """ Display the current aoi on a map and remove the dc

        Args:

            map_ (SepalMap): Map to display the element

        """
        aoi = ee.FeatureCollection(self.assetId)
        map_.zoom_ee_object(aoi.geometry())
        map_.addLayer(aoi, {'color': 'green'}, name='aoi')
        
        #the aoi map have a dc
        map_.dc.clear()
        
        try:
            map_.remove_control(map_.dc)
        except:
            pass
        
        return self


    def get_bounds(self, ee_asset, cardinal=False):
        """ Returns the min(lon,lat) and max(lon, lat) from the given asset

        Args:
            ee_asset (ee.object): GEE asset (FeatureCollection, Geometry)
            cardinal (boolean) (optional)


        Returns:
            If cardinal True: returns cardinal points tl, bl, tr, br
            If cardinal False: returns bounding box
        """

        # 
        ee_bounds = ee.FeatureCollection(ee_asset).geometry().bounds().coordinates()
        coords = ee_bounds.get(0).getInfo()
        ll, ur = coords[0], coords[2]

        # Get the bounding box
        min_lon, min_lat, max_lon, max_lat = ll[0], ll[1], ur[0], ur[1]


        # Get (x, y) of the 4 cardinal points
        tl = (min_lon, max_lat)
        bl = (min_lon, min_lat)
        tr = (max_lon, max_lat)
        br = (max_lon, min_lat)

        if cardinal:
            return tl, bl, tr, br

        return min_lon, min_lat, max_lon, max_lat
    
    def get_aoi_shp(self, dwnDir=''):

        aoi_name = Path(self.assetId).stem.replace('aoi_', '')
        filename = '{0}{1}.shp'.format(dwnDir, aoi_name)
    
        if os.path.isfile(filename):
            return filename
    
        # verify that the asset exist
        aoi = ee.FeatureCollection(self.assetId)
    
        # convert into shapely
        aoiJson = geemap.ee_to_geojson(aoi)
        aoiShp = sg.shape(aoiJson['features'][0]['geometry'])
    
        # Now convert it to a shapefile with OGR    
        driver = ogr.GetDriverByName('Esri Shapefile')
        ds = driver.CreateDataSource(filename)
        layer = ds.CreateLayer('', None, ogr.wkbPolygon)

        # Add one attribute
        layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
        defn = layer.GetLayerDefn()

        # Create a new feature (attribute and geometry)
        feat = ogr.Feature(defn)
        feat.SetField('id', 123)
    
        # Make a geometry, from Shapely object
        geom = ogr.CreateGeometryFromWkb(aoiShp.wkb)
        feat.SetGeometry(geom)
    
        layer.CreateFeature(feat)
    
        # Save and close everything
        ds = layer = feat = geom = None
    
        #add the spatial referecence
        spatialRef = osr.SpatialReference()
        spatialRef.ImportFromEPSG(4326)
    
        spatialRef.MorphToESRI()
        file = open('{0}{1}.prj'.format(dwnDir, aoi_name), 'w')
        file.write(spatialRef.ExportToWkt())
        file.close()
    
        return filename
    
    def get_aoi_name(self):
        
        if not self.assetId: return None
        
        path = Path(self.assetId).stem
        
        return path.replace('aoi_', '')
    
class TileAoi(sw.Tile):
    """render and bind all the variable to create an autonomous aoi selector. It will create a asset in you gee account with the name 'aoi_[aoi_name]'. The assetId will be added to io.assetId."""
    
    #constants
    SELECTION_METHOD =('Country boundaries', 'Draw a shape', 'Upload file', 'Use GEE asset')
    
    def __init__(self, io, **kwargs):
        
        #create the output
        aoi_output = sw.Alert().add_msg(ms.AOI_MESSAGE)
        
        #create the inputs widgets 
        aoi_file_input = sw.FileInput(['.shp']).hide()
        aoi_output.bind(aoi_file_input, io, 'file_input')
    
        aoi_file_name = v.TextField(
            label='Select a filename', 
            v_model=io.file_name,
            class_='d-none'
        )
        aoi_output.bind(aoi_file_name, io, 'file_name')
    
        aoi_country_selection = v.Select(
            items=[*su.create_FIPS_dic()], 
            label='Country/Province', 
            v_model=None,
            class_='d-none'
        )
        aoi_output.bind(aoi_country_selection, io, 'country_selection')
    
        aoi_asset_name = v.TextField(
            label='Select a GEE asset', 
            v_model=None,
            class_='d-none'
        )
        aoi_output.bind(aoi_asset_name, io, 'assetId')
    
        widget_list = [
            aoi_file_input, 
            aoi_file_name, 
            aoi_country_selection, 
            aoi_asset_name
        ]
        
        #create the map 
        m = SepalMap(['Esri Satellite', 'CartoDB.Positron'], dc=True)
        self.handle_draw(m.dc, io, 'drawn_feat', aoi_output)
    
        #bind the input to the selected method 
        aoi_select_method = v.Select(items=self.SELECTION_METHOD, label='AOI selection method', v_model=None)
        self.bind_aoi_method(aoi_select_method, widget_list, io, m, m.dc, self.SELECTION_METHOD)
    

        #create the validation button 
        aoi_select_btn = sw.Btn('Select these inputs')
        self.bind_aoi_process(aoi_select_btn, io, m, m.dc, aoi_output, self.SELECTION_METHOD)
    
        #assemble everything on a tile 
        inputs = v.Layout(
            _metadata={'mount-id': 'data-input'},
            class_="pa-5",
            row=True,
            align_center=True, 
            children=[
                v.Flex(xs12=True, children=[aoi_select_method]),
                v.Flex(xs12=True, children=[aoi_country_selection]),
                v.Flex(xs12=True, children=[aoi_file_input]),
                v.Flex(xs12=True, children=[aoi_file_name]),
                v.Flex(xs12=True, children=[aoi_asset_name]),
                v.Flex(xs12=True, children=[aoi_select_btn]),
                v.Flex(xs12=True, children=[aoi_output]),
            ]
        )
        
        aoi_content_main = v.Layout(
            row=True,
            xs12=True,
            children = [
                v.Flex(xs12=True, md6=True, children=[inputs]),
                v.Flex(class_="pa-5", xs12=True, md6=True, children=[m])
            ]
        )
        
        super().__init__(
            id_='aoi_widget',
            title='AOI selection', 
            inputs=[aoi_content_main]
        )
        
    def handle_draw(self, dc, io, variable, output):
        """ 
        handle the drawing of a geometry on a map. The geometry is transform into a ee.featurecollection and send to the variable attribute of obj.
    
        Args: 
            dc (DrawControl) : the draw control on which the drawing will be done 
            io (obj Aoi_io) : any object created for IO of your tile 
            variable (str) : the name of the atrribute of the obj object where to store the ee.FeatureCollection 
            output (sw.Alert) : the output to display results
        
    """
        def on_draw(self, action, geo_json, obj, variable, output):
            geom = geemap.geojson_to_ee(geo_json, False)
            feature = ee.Feature(geom)
            setattr(obj, variable, ee.FeatureCollection(feature)) 
            
            output.add_live_msg('A shape have been drawn')

            return 
        
        
        dc.on_draw(partial(
            on_draw,
            obj=io,
            variable=variable,
            output=output
        ))
    
        return self
    
    def bind_aoi_process(self, btn, io, m, dc, output, list_method):
        """
        Create an asset in your gee acount and serve it to the map.
        
        Args:
            btn (v.Btn) : the btn that launch the process
            io (Aoi_IO) : the IO of the aoi selection tile
            m (geemap.Map) : the tile map
            dc (drawcontrol) : the drawcontrol
            output (v.Alert) : the alert of the selector tile
            list_method([str]) : the list of the available selections methods
        """
    
        def on_click(widget, event, data, io, m, dc, output, list_method):
        
            widget.toggle_loading()
        
            #create the aoi asset
            assetId = run_aoi_selection.run_aoi_selection(
                file_input        = io.file_input, 
                file_name         = io.file_name, 
                country_selection = io.country_selection, 
                asset_name        = io.assetId, 
                drawn_feat        = io.drawn_feat,
                drawing_method    = io.selection_method,
                widget_alert      = output, 
                list_method       = list_method, 
            )
            
            #remove the dc
            dc.clear()
            try:
                m.remove_control(dc)
            except:
                pass
        
            #display it on the map
            if assetId:
                setattr(io, 'assetId', assetId)
                io.display_on_map(m)
            
            widget.toggle_loading()
        
            return 
    
        btn.on_event('click', partial(
            on_click,
            io          = io, 
            m           = m, 
            dc          = dc, 
            output      = output,
            list_method = list_method
        ))
    
        return self
    
    def bind_aoi_method(self, method_widget, list_input, obj, m, dc, selection_method):
        """
        change the display of the AOI selector according to the method selected. will only display the useful one
        
        Args: 
            method_widget (v.select) : the method selector widget 
            list_input ([v.widget]) : the list of all the aoi inputs
            obj (Aoi_IO) : the IO object of the tile
            m (geemap.Map) the map displayed in the tile
            dc (DrawControl) : the drawing control
            selection_method ([str]) : the available selection methods
        """
        
        def on_change(widget, event, data, list_input, obj, m, dc, selection_method):
            
            #clearly identify the differents widgets 
            aoi_file_input = list_input[0]
            aoi_file_name = list_input[1]
            aoi_country_selection = list_input[2]
            aoi_asset_name = list_input[3]
            
            setattr(obj, 'selection_method', widget.v_model)
            
            #remove the dc 
            dc.clear()
            try:
                m.remove_control(dc)
            except:
                pass
            #toogle the appropriate inputs
            if widget.v_model == selection_method[0]: #country selection
                self.toggle_inputs([aoi_country_selection], list_input)
            elif widget.v_model == selection_method[1]: #drawing
                self.toggle_inputs([aoi_file_name], list_input)
                m.add_control(dc)
            elif widget.v_model == selection_method[2]: #shp file
                self.toggle_inputs([aoi_file_input], list_input)
            elif widget.v_model == selection_method[3]: #gee asset
                self.toggle_inputs([aoi_asset_name], list_input)
        
        
        
        method_widget.on_event('change', partial(
            on_change,
            list_input=list_input,
            obj=obj,
            m=m,
            dc=dc, 
            selection_method=selection_method
        ))
        
        return self 