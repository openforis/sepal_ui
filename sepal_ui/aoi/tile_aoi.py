from functools import partial
from pathlib import Path
import json
from datetime import datetime

import ipyvuetify as v
import geemap
import ee
import pandas as pd

from sepal_ui.aoi.aoi_io import Aoi_io
from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su, run_aoi_selection
from sepal_ui.mapping import SepalMap
from sepal_ui.message import ms
    
# initialize earth engine
su.init_ee()
    
class FileNameField(v.TextField, sw.SepalWidget):
    """
    custom v.TextField heriting from sw.SepalWidget. default_name will be used as default v_model
    
    Args:
        default_name (str): a default name
    """
    
    def __init__(self, default_name = None):
        
        super().__init__(
            label   = ms.aoi_sel.asset_name_lbl, 
            v_model = default_name
        )
        
class Adm0Select(v.Select, sw.SepalWidget):
    """ 
    Custom v.Select heriting from sw.SepalWidget. Uses the FAO GAUL 2015 admo0_name features as item
    """
    
    def __init__(self):
        country_codes = Path(__file__).parents[1].joinpath('scripts/country_code.csv')
        country_codes = pd.read_csv(country_codes)
        country_codes = country_codes.drop_duplicates(subset=['ADM0_CODE'])
        country_codes = country_codes.sort_values('ADM0_NAME')
        
        items = []
        for i, row in country_codes.iterrows():
            items.append({'text': row.ADM0_NAME, 'value': row.ADM0_CODE})
        
        country_codes = None
        
        super().__init__(
            items   = items, 
            label   = ms.aoi_sel.country_lbl, 
            v_model = None,
            dense = True
        )
        
class Adm1Select(v.Select, sw.SepalWidget):
    """ 
    Custom v.Select heriting from sw.SepalWidget. Uses the FAO GAUL 2015 admo1_name features as item
    """
    
    def __init__(self):
        
        super().__init__(
            items   = [], 
            label   = ms.aoi_sel.adm1_lbl, 
            v_model = None,
            dense = True
        )
        
    def set_admin_input(self, change):
        """set the list of possible items to the list of corresponding GAUL admo1_code - name"""
        
        adm0_code = change['new']
        
        # filter the country list to keep only each admin1 in the selected admin0
        country_codes = Path(__file__).parents[1].joinpath('scripts/country_code.csv')
        country_codes = pd.read_csv(country_codes)
        country_codes = country_codes[country_codes['ADM0_CODE'] == adm0_code]        
        country_codes = country_codes.drop_duplicates(subset=['ADM1_CODE'])
        country_codes = country_codes.sort_values('ADM1_NAME')
        
        # create a usable dict for the items
        items = []
        for i, row in country_codes.iterrows():
            items.append({'text': row.ADM1_NAME, 'value': row.ADM1_CODE})
        
        country_codes = None
        
        # set the items 
        self.items = items
        
        return self
        
        
class Adm2Select(v.Select, sw.SepalWidget):
    """ 
    Custom v.Select heriting from sw.SepalWidget. Uses the FAO GAUL 2015 admo0_name features as item
    """
    
    def __init__(self):
        
        super().__init__(
            items   = [], 
            label   = ms.aoi_sel.adm2_lbl, 
            v_model = None,
            dense = True
        )
        
    def set_admin_input(self, change):
        """set the list of possible items to the list of corresponding GAUL admo1_code - name"""
        
        adm1_code = change['new']
        
        # filter the country list to keep only each admin1 in the selected admin0
        country_codes = Path(__file__).parents[1].joinpath('scripts/country_code.csv')
        country_codes = pd.read_csv(country_codes)
        country_codes = country_codes[country_codes['ADM1_CODE'] == adm1_code]
        country_codes = country_codes.sort_values('ADM2_NAME')
        
        # create a usable dict for the items
        items = []
        for i, row in country_codes.iterrows():
            items.append({'text': row.ADM2_NAME, 'value': row.ADM2_CODE})
        
        country_codes = None
        
        # set the items 
        self.items = items
        
        return self
        
class MethodSelect(v.Select, sw.SepalWidget):
    """
    Custom v.Select heriting from sw.SepalWidget. create a method list based on the provided methods and default methods. 
    2 headers will be added (if relevant), on before the administrative selection methods, another before the custom asset/shape/points methods.
    if no list is provided the default_methods list will be used entirely.
    
    Args: 
        default_methods ([str]): the list of all methods name that we can to display
        methods ([str], optionnal): the list of all methods name that we want to display
         
    """
    
    def __init__(self, default_methods, methods=None):
        
        # get all the methods if none 
        methods = methods or default_methods
        
        # create a custom item list 
        items = []
        custom_header = True
        admin_header = True
        for m in methods:
            
            if m in default_methods:
                
                # admin header
                if m in default_methods[:3] and admin_header: 
                    items.append({'header': ms.aoi_sel.administrative})
                    admin_header = False
                elif m in default_methods[3:] and custom_header:
                    items.append({'header': ms.aoi_sel.custom})
                    custom_header = False
                        
                items.append({'text': m, 'value': m})
                
        # create the input 
        super().__init__(
            label = ms.aoi_sel.method_lbl,
            items = items,
            v_model = None,
            dense = True
        )
        
class TileAoi(sw.Tile):
    """
    sw.Tile tailored for the selection of an aoi. it is meant to be used with the aoi.Aoi_Io object.
    Render and bind all the variable to create an autonomous aoi selector. 
    If you use a custom aoi, it will create a asset in you gee account with the name 'aoi_[aoi_name]'.
    
    Args:
        io (aoi.Aoi_Io): an object that will carry the inputs and outputs of the tile
        methods ([str]): the methods to use for the aoi selection. needs to be part of the Private const SELECTION_METHOD
        folder (str | pathlib.path): the earthengine folder to use for asset saving and discovery. default to user Root
        
    Attributes: 
        io (aoi.aoi_Io): the aoi_io used to store aoi selection inputs and outputs
        
        aoi_output (sw.Alert): the Alert widget used to display information
        
        folder (str | pathlib.Path): the earthengine folder to use for asset saving and discovery. default to user Root
        
        aoi_file_name (FileNameField): a TextField input to choose asset name
        aoi_file_input (sw.FileInput): a file selector to retrieve sepal folders 
        aoi_country_selection (CountrySelect): the country selector input
        aoi_asset_name (sw.AssetSelect): a ComboBox input to select an asset in the self.folder or any custom asset link
        aoi_load_table (sw.LoadTableField): a table input field to retreive information from a point file
        aoi_select_method (v.Select): the input to select to aoi selection method to use. change the display of the tile widgets
        aoi_select_btn (sw.Btn): the Btn to launch the exportation of an asset
        
        m (ms.SepalMap): The map to display drawings and selected aoi. It is using both sattelites and CartoDb.DarkMatter basemaps
    """
    
    # constants
    SELECTION_METHOD =['Country boundaries', "First administrative layer", 'second administrative layer', 'Draw a shape', 'Use GEE asset', 'Upload file', 'Use points file']
    
    def __init__(self, io, methods = SELECTION_METHOD, folder = None, **kwargs):
        
        # load the io 
        self.io = io
        
        # create the output
        self.aoi_output = sw.Alert()
        
        # save the folder (mainly for testing purposes)
        self.folder = folder
        
        # create the inputs widgets 
        self.aoi_file_name = FileNameField(io.file_name).hide()     
        self.aoi_file_input = sw.FileInput(['.shp']).hide()
        self.aoi_country_selection = Adm0Select().hide()
        self.aoi_admin_1_select = Adm1Select().hide()
        self.aoi_admin_2_select = Adm2Select().hide()
        self.aoi_asset_name = sw.AssetSelect(folder = self.folder, default_asset = io.default_asset).hide()
        self.aoi_load_table = sw.LoadTableField().hide()
        
        # bind to aoi_io 
        self.aoi_output = sw.Alert() \
            .bind(self.aoi_file_name, self.io, 'file_name',  verbose=False) \
            .bind(self.aoi_file_input, self.io, 'file_input',  verbose=False) \
            .bind(self.aoi_country_selection, self.io, 'adm0',  verbose=False) \
            .bind(self.aoi_admin_1_select, self.io, 'adm1',  verbose=False) \
            .bind(self.aoi_admin_2_select, self.io, 'adm2',  verbose=False) \
            .bind(self.aoi_asset_name, self.io, 'assetId',  verbose=False) \
            .bind(self.aoi_load_table, self.io, 'json_csv',  verbose=False)
    
        widget_list = [
            self.aoi_file_name, 
            self.aoi_file_input, 
            self.aoi_country_selection, 
            self.aoi_admin_1_select,
            self.aoi_admin_2_select,
            self.aoi_asset_name,
            self.aoi_load_table
        ]
        
        #create the map 
        self.m = SepalMap(['Esri Satellite', 'CartoDB.DarkMatter'], dc=True)
    
        # bind the input to the selected method 
        #method_items = [m for m in methods if m in self.SELECTION_METHOD] 
        self.aoi_select_method = MethodSelect(self.SELECTION_METHOD, methods)
        
        # create the validation button 
        self.aoi_select_btn = sw.Btn(ms.aoi_sel.btn)
    
        # assemble everything on a tile 
        inputs = v.Layout(
            class_       = "pa-5",
            row          = True,
            align_center = True, 
            children     = (
                [v.Flex(xs12 = True, children =[self.aoi_select_method])] 
                + [v.Flex(xs12 = True, children = [widget]) for widget in widget_list]
                + [v.Flex(xs12 = True, children =[self.aoi_select_btn])] 
                + [v.Flex(xs12 = True, children = [self.aoi_output])]
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
        
        super().__init__(id_ = 'aoi_widget', title = ms.aoi_sel.title, inputs = [aoi_content_main])
        
        # link the custom behaviours 
        self.aoi_load_table.observe(self._on_table_change, 'v_model')
        self.aoi_file_input.observe(self._on_file_change, 'v_model')
        self.m.dc.on_draw(self.handle_draw)
        self.aoi_select_method.observe(partial(self.bind_aoi_method, list_input = widget_list), 'v_model')
        self.aoi_select_btn.on_event('click', self.bind_aoi_process)
        self.aoi_country_selection.observe(self.aoi_admin_1_select.set_admin_input, 'v_model')
        self.aoi_admin_1_select.observe(self.aoi_admin_2_select.set_admin_input, 'v_model')
        
    def handle_draw(self, dc, action, geo_json):
        """
        handle the drawing of a geometry on a map. 
        The geometry is transform into a ee.featurecollection and save in self.io
        
        Args:
            dc (geemap.DrawingControl): the drawing control
            action (): the action that fire this handler
            geo_json (json): the dict of the drawn feature
            
        Return:
            self
        """
        
        # change the date 
        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.aoi_file_name.v_model = f'Manual_{date}'
        
        # add the feature
        geom = geemap.geojson_to_ee(geo_json, False)
        feature = ee.Feature(geom)
        self.io.drawn_feat = ee.FeatureCollection(feature)
            
        self.aoi_output.add_live_msg(ms.aoi_sel.shape_drawn)

        return self
    
    def bind_aoi_process(self, widget, event, data):
        """
        Use the user inputs to create a aoi. If a administrative layer have been selected, then its features are saved in self.io.
        If it's a custom selection method, a custom asset is created under `aoi_[aoi_name]` in the self.folder of the user GEE account.
        The final aoi will be displayed on the map 
        
        Args:
            widget (v.Vue): the vuetify object that trigger the binding
            event (str): the event that trigger the binding
            data ({str}): the data of the javascript event
            
        Return:
            self
        """
        
        # lock the btn
        widget.toggle_loading()            
            
        try:
            # create the aoi asset
            run_aoi_selection.run_aoi_selection(
                output      = self.aoi_output, 
                list_method = self.SELECTION_METHOD, 
                io          = self.io,
                folder      = self.folder
            )
            
            # display the resulting aoi on the map
            if self.io.get_aoi_ee():
                self.m.hide_dc()
                self.io.display_on_map(self.m)
            
        except Exception as e: 
            self.aoi_output.add_live_msg(str(e), 'error') 
        
        # free the btn
        widget.toggle_loading()
    
        return self
    
    def bind_aoi_method(self, change, list_input):
        """
        change the display of the AOI selector according to the method selected. will only display the useful inputs
        
        Args:
            change ({obj}): the change dictionnary of an observe method (see Traitlet documentation)
            list_input ([v.Vue]): the list of all the inputs of the aoi selector
            
        Return:
            self
        """
        
        # reset the aoi_io
        self.io.clear_attributes()
        
        # clearly identify the differents widgets 
        aoi_file_input        = list_input[1]
        aoi_file_name         = list_input[0]
        aoi_admin_0_select    = list_input[2]
        aoi_admin_1_select    = list_input[3]
        aoi_admin_2_select    = list_input[4]
        aoi_asset_name        = list_input[5]
        aoi_load_table        = list_input[6]
        
        # clear all the v_model
        aoi_file_name.v_model = None
        aoi_admin_0_select.v_model = None
        aoi_asset_name.v_model = None
        aoi_admin_1_select.items = []
        aoi_admin_2_select.items = []
        
        # extract the selecion methods
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
            self.toggle_inputs([aoi_admin_0_select], list_input)
        # admin 1
        elif change['new'] == method[1]: 
            self.toggle_inputs([aoi_admin_0_select, aoi_admin_1_select], list_input)
        # admin 2
        elif change['new'] == method[2]: 
            self.toggle_inputs([aoi_admin_0_select, aoi_admin_1_select, aoi_admin_2_select], list_input)
        # drawing
        elif change['new'] == method[3]: 
            self.toggle_inputs([aoi_file_name], list_input)
            self.m.show_dc()
        # gee asset
        elif change['new'] == method[4]: 
            self.toggle_inputs([aoi_asset_name], list_input)
        # shp file
        elif change['new'] == method[5]: 
            self.toggle_inputs([aoi_file_name, aoi_file_input], list_input)
        # Point file (.csv)
        elif change['new'] == method[6]: 
            self.toggle_inputs([aoi_file_name, aoi_load_table], list_input)
        # display nothing 
        else:
            self.toggle_inputs([], list_input)
        
        return self 
    
    def _on_file_change(self, change):
        """
        Change the aoi_file_name v_model with a pattern based on the file name
        the following pattern is used : 'aoi_[file_path.stem]'
        
        Args:
            change ({obj}): the change dictionnary of an observe method (see Traitlet documentation)
            
        Return:
            self
        """
        
        name = Path(change['new']).stem
        self.aoi_file_name.v_model = name
        
        return
    
    def _on_table_change(self, change):
        """
        Change the aoi_file_name v_model with a pattern based on the file name
        the following pattern is used : 'aoi_[file_path.stem]'
        
        Args:
            change ({obj}): the change dictionnary of an observe method (see Traitlet documentation)
            
        Return:
            self
        """
        
        load_df = json.loads(change['new'])
        
        name = Path(load_df['pathname']).stem
        self.aoi_file_name.v_model = name
        
        return
    