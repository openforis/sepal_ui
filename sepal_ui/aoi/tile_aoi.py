from functools import partial
from pathlib import Path
import json
from datetime import datetime

import ipyvuetify as v
import geemap
import ee

from .aoi_io import Aoi_io
from .. import sepalwidgets as sw
from ..scripts import utils as su, run_aoi_selection
from ..mapping import SepalMap
    
# initialize earth engine
su.init_ee()
    
class FileNameField(v.TextField, sw.SepalWidget):
    
    def __init__(self, default_name = ''):
        
        super().__init__(
            label   = 'Select an asset name', 
            v_model = default_name
        )
        
class CountrySelect(v.Select, sw.SepalWidget):
    
    def __init__(self):
        
        super().__init__(
            items   = [*su.get_gaul_dic()], 
            label   = 'Country/Province', 
            v_model = None
        )
        
class TileAoi(sw.Tile):
    """render and bind all the variable to create an autonomous aoi selector. It will create a asset in you gee account with the name 'aoi_[aoi_name]'. The assetId will be added to io.assetId.
    
    available selection methods : 'Country boundaries', 'Draw a shape', 'Upload file', 'Use GEE asset', 'Use points file'
    """
    
    # constants
    SELECTION_METHOD =('Country boundaries', 'Draw a shape', 'Upload file', 'Use GEE asset', 'Use points file')
    
    def __init__(self, io, methods = SELECTION_METHOD, folder = None, **kwargs):
        
        # load the io 
        self.io = io
        
        # create the output
        self.output = sw.Alert()#.add_msg(ms.AOI_MESSAGE)
        
        # save the folder (mainly for testing purposes)
        self.folder = folder
        
        # create the inputs widgets 
        self.aoi_file_name = FileNameField(io.file_name).hide()
        self.output.bind(self.aoi_file_name, self.io, 'file_name')
        
        self.aoi_file_input = sw.FileInput(['.shp']).hide()
        self.output.bind(self.aoi_file_input, self.io, 'file_input')
        self.aoi_file_input.observe(self._on_file_change, 'v_model')
        
        self.aoi_country_selection = CountrySelect().hide()
        self.output.bind(self.aoi_country_selection, self.io, 'country_selection')
    
        self.aoi_asset_name = sw.AssetSelect(folder = self.folder).hide()
        self.output.bind(self.aoi_asset_name, self.io, 'assetId')
        
        self.aoi_load_table = sw.LoadTableField().hide()
        self.output.bind(self.aoi_load_table, self.io, 'json_csv')
        self.aoi_load_table.observe(self._on_table_change, 'v_model')
    
        widget_list = [
            self.aoi_file_name, 
            self.aoi_file_input, 
            self.aoi_country_selection, 
            self.aoi_asset_name,
            self.aoi_load_table
        ]
        
        #create the map 
        self.m = SepalMap(['Esri Satellite', 'CartoDB.DarkMatter'], dc=True)
        self.m.dc.on_draw(self.handle_draw)
    
        # bind the input to the selected method 
        method_items = [m for m in methods if m in self.SELECTION_METHOD] 
        self.aoi_select_method = v.Select(items = method_items, label = 'AOI selection method', v_model = None)
        self.aoi_select_method.observe(partial(self.bind_aoi_method, list_input = widget_list), 'v_model')
        
        # create the validation button 
        self.aoi_select_btn = sw.Btn('Select these inputs')
        self.aoi_select_btn.on_event('click', self.bind_aoi_process)
    
        # assemble everything on a tile 
        inputs = v.Layout(
            _metadata    = {'mount-id': 'data-input'},
            class_       = "pa-5",
            row          = True,
            align_center = True, 
            children     = (
                [v.Flex(xs12 = True, children =[self.aoi_select_method])] 
                + [v.Flex(xs12 = True, children = [widget]) for widget in widget_list]
                + [v.Flex(xs12 = True, children =[self.aoi_select_btn])] 
                + [v.Flex(xs12 = True, children = [self.output])]
            )
        )
        
        aoi_content_main = v.Layout(
            row      = True,
            xs12     = True,
            children = [
                v.Flex(xs12 = True, md6 = True, children = [inputs]),
                v.Flex(xs12 = True, md6 = True, class_ = "pa-5", children = [self.m])
            ]
        )
        
        super().__init__(id_ = 'aoi_widget', title = 'AOI selection', inputs = [aoi_content_main])
        
    def handle_draw(self, dc, action, geo_json):
        """handle the drawing of a geometry on a map. The geometry is transform into a ee.featurecollection and send to the variable attribute of self.io"""
        
        # change the date 
        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.aoi_file_name.v_model = f'Manual_{date}'
        
        # add the feature
        geom = geemap.geojson_to_ee(geo_json, False)
        feature = ee.Feature(geom)
        self.io.drawn_feat = ee.FeatureCollection(feature)
            
        self.output.add_live_msg('A shape have been drawn')

        return self
    
    def bind_aoi_process(self, widget, event, data):
        """Create an asset in your gee acount and serve it to the map."""
        
        widget.toggle_loading()            
            
        try:
            # create the aoi asset
            run_aoi_selection.run_aoi_selection(
                output      = self.output, 
                list_method = self.SELECTION_METHOD, 
                io          = self.io,
                folder      = self.folder
            )
            
            # display the resulting aoi on the map
            if self.io.assetId or self.io.feature_collection:
                self.m.hide_dc()
                self.io.display_on_map(self.m)
            
        except Exception as e: 
            self.output.add_live_msg(str(e), 'error') 
            
        widget.toggle_loading()
    
        return self
    
    def bind_aoi_method(self, change, list_input):
        """change the display of the AOI selector according to the method selected. will only display the useful one"""
            
        # clearly identify the differents widgets 
        aoi_file_input        = list_input[1]
        aoi_file_name         = list_input[0]
        aoi_country_selection = list_input[2]
        aoi_asset_name        = list_input[3]
        aoi_load_table        = list_input[4]
        
        # clear the file_name
        aoi_file_name.v_model = None
        
        # extract the selecion_method
        method = self.SELECTION_METHOD
            
        # update the io
        self.io.selection_method = change['new']
            
        # hide the dc
        self.m.hide_dc()
        
        #############################################
        ##      toogle the appropriate inputs      ##
        #############################################
            
        # country selection
        if change['new'] == method[0]: 
            self.toggle_inputs([aoi_country_selection], list_input)
        # drawing
        elif change['new'] == method[1]: 
            self.toggle_inputs([aoi_file_name], list_input)
            self.m.show_dc()
        # shp file
        elif change['new'] == method[2]: 
            self.toggle_inputs([aoi_file_name, aoi_file_input], list_input)
        # gee asset
        elif change['new'] == method[3]: 
            self.toggle_inputs([aoi_asset_name], list_input)
        # Point file (.csv)
        elif change['new'] == method[4]: 
            self.toggle_inputs([aoi_file_name, aoi_load_table], list_input)
        # display nothing 
        else:
            self.toggle_inputs([], list_input)
        
        return self 
    
    def _on_file_change(self, change):
        
        name = Path(change['new']).stem
        self.aoi_file_name.v_model = name
        
        return
    
    def _on_table_change(self, change):
        
        load_df = json.loads(change['new'])
        
        name = Path(load_df['pathname']).stem
        self.aoi_file_name.v_model = name
        
        return
    