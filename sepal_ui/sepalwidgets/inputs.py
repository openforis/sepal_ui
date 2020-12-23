import os 
from pathlib import Path
import json

import ipyvuetify as v
from traitlets import HasTraits, Unicode, link
from ipywidgets import jslink
import pandas as pd
import ee

from sepal_ui.frontend.styles import *
from sepal_ui.scripts import utils as su
from sepal_ui.sepalwidgets.sepalwidget import SepalWidget
from sepal_ui.sepalwidgets.btn import Btn

# initialize earth engine
su.init_ee()

class DatePicker(v.Layout, SepalWidget):
    
    def __init__(self, label="Date", **kwargs):
        
        date_picker = v.DatePicker(
            no_title = True, 
            v_model = None, 
            scrollable = True
        )

        date_text = v.TextField(
            v_model = None,
            label = label,
            hint = "YYYY-MM-DD format",
            persistent_hint = True, 
            prepend_icon = "event",
            readonly = True,
            v_on = 'menuData.on'
        )

        self.menu = v.Menu(
            min_width="290px",
            transition = "scale-transition",
            offset_y = True, 
            value = False,
            close_on_content_click = False,
            children = [date_picker],
            v_slots = [{
                'name': 'activator',
                'variable': 'menuData',
                'children': date_text,
            }]
        )

        super().__init__(
            v_model = None,
            row = True,
            class_ = 'pa-5',
            align_center = True,
            children = [v.Flex(xs10=True, children=[self.menu])],
            **kwargs
        )

        jslink((date_picker, 'v_model'), (date_text, 'v_model'))
        jslink((date_picker, 'v_model'), (self, 'v_model'))
        
        #close the datepicker on click
        #date_text.observe(lambda _: setattr(self.menu, 'value', False), 'v_model')
        
class FileInput(v.Flex, SepalWidget, HasTraits):

    file = Unicode('')
    
    def __init__(self, extentions = [], folder=os.path.expanduser('~'), label='search file', v_model = None, **kwargs):

        self.extentions = extentions
        self.folder = folder
        
        self.selected_file = v.TextField(
            readonly = True,
            label    = 'Selected file', 
            class_   = 'ml-5 mt-5',
            v_model  = self.file
        )

        self.loading = v.ProgressLinear(
            indeterminate    = False, 
            background_color = 'grey darken-3',
            color            = COMPONENTS['PROGRESS_BAR']['color']
            )
        
        self.file_list = v.List(
            dense      = True, 
            color      = 'grey darken-3',
            flat       = True,
            max_height = '300px',
            style_     = 'overflow: auto; border-radius: 0 0 0 0;',
            children   = [ 
                v.ListItemGroup(
                    children = self._get_items(),
                    v_model  = ''
                )
            ]
        )

        self.file_menu = v.Menu(
            min_width              = 300,
            children               = [self.loading, self.file_list], 
            close_on_content_click = False,
            v_slots                = [{
                'name': 'activator',
                'variable': 'x',
                'children': Btn(icon='mdi-file-search', v_model=False, v_on='x.on', text=label)
        }])
        
        self.reload = v.Btn(
            icon = True,
            color = 'primary',
            children = [v.Icon(children=['mdi-cached'])]
        )
        
        super().__init__(
            row          = True,
            class_       = 'd-flex align-center mb-2',
            align_center = True,
            children     = [
                self.reload,
                self.file_menu,
                self.selected_file,
            ],
            **kwargs
        )
        
        link((self.selected_file, 'v_model'), (self, 'file'))
        link((self.selected_file, 'v_model'), (self, 'v_model'))

        self.file_list.children[0].observe(self._on_file_select, 'v_model')
        self.reload.on_event('click', self._on_reload)
        
    def _on_file_select(self, change):
        new_value = change['new']
        if new_value:
            if os.path.isdir(new_value):
                self.folder = new_value
                self._change_folder()
                
            elif os.path.isfile(new_value):
                self.file = new_value
            
            return
                
    def _change_folder(self):
        """change the target folder"""
        #reset files
        self.file_list.children[0].children = self._get_items()
    

    def _get_items(self):
        """return the list of items inside the folder"""

        self.loading.indeterminate = not self.loading.indeterminate
        
        folder = Path(self.folder)

        list_dir = [el for el in folder.glob('*/') if not el.name.startswith('.')]

        if self.extentions:
            list_dir = [el for el in list_dir if el.is_dir() or el.suffix in self.extentions]

        folder_list = []
        file_list = []

        for el in list_dir:
            
            if el.suffix in ICON_TYPES.keys():
                icon = ICON_TYPES[el.suffix]['icon']
                color = ICON_TYPES[el.suffix]['color']
            else:
                icon = ICON_TYPES['DEFAULT']['icon']
                color = ICON_TYPES['DEFAULT']['color']
            
            children = [
                v.ListItemAction(children=[v.Icon(color= color,children=[icon])]),
                v.ListItemContent(children=[v.ListItemTitle(children=[el.stem + el.suffix])]),
            ] 

            if el.is_dir():
                folder_list.append(v.ListItem(value=str(el), children=children))
            else:
                file_size = su.get_file_size(el)
                children.append(v.ListItemActionText(children=[file_size]))
                file_list.append(v.ListItem(value=str(el), children=children))

        folder_list = sorted(folder_list, key=lambda x: x.value)
        file_list = sorted(file_list, key=lambda x: x.value)

        parent_path = str(folder.parent)
        parent_item = v.ListItem(
            value=parent_path, 
            children=[
                v.ListItemAction(children=[v.Icon(color=ICON_TYPES['PARENT']['color'], children=[ICON_TYPES['PARENT']['icon']])]),
                v.ListItemContent(children=[v.ListItemTitle(children=[f'..{parent_path}'])]),
            ]
        )

        folder_list.extend(file_list)
        folder_list.insert(0,parent_item)

        self.loading.indeterminate = not self.loading.indeterminate
        
        return folder_list
    
    def _on_reload(self, widget, event, data):
        
        # force the update of the current folder
        self._change_folder()
        
        return

class LoadTableField(v.Col, SepalWidget):
    
    default_v_model = {
            'pathname'  : None, 
            'id_column' : None, 
            'lat_column': None, 
            'lng_column': None
    }
    
    def __init__(self):
        
        self.fileInput = FileInput(['.csv', '.txt'])
                
        self.IdSelect = self._LocalSelect('id_column', 'Id')
        self.LngSelect = self._LocalSelect('lng_column', 'Longitude')
        self.LatSelect = self._LocalSelect('lat_column', 'Latitude')
        
        super().__init__(
            v_model = json.dumps(self.default_v_model),
            children = [
                self.fileInput,
                self.IdSelect,
                self.LngSelect,
                self.LatSelect
            ]
        )
        
        # link the dropdowns
        jslink((self.IdSelect, 'items'),(self.LngSelect, 'items'))
        jslink((self.IdSelect, 'items'),(self.LatSelect, 'items'))
        
        # link the widget with v_model 
        self.fileInput.observe(self._on_file_input_change, 'v_model')
        self.IdSelect.observe(self._on_select_change, 'v_model')
        self.LngSelect.observe(self._on_select_change, 'v_model')
        self.LatSelect.observe(self._on_select_change, 'v_model')
        
    def _on_file_input_change(self, change):
        
        path = change['new']
            
        df = pd.read_csv(path, sep=None, engine='python')
        
        if len(df.columns) < 3: 
            self._clear_select()
            return 
        
        self._set_value('pathname', path)
        
        # clear the selects
        self._clear_select()
        self.IdSelect.items = df.columns.tolist()
        
        # pre load values that sounds like what we are looking for 
        # it will only keep the first occurence of each one 
        for name in reversed(df.columns.tolist()):
            lname = name.lower() 
            if 'id' in lname:
                self.IdSelect.v_model = name
            elif any(ext in lname for ext in ['lng', 'long', 'longitude', 'x_coord', 'xcoord']):
                self.LngSelect.v_model = name
            elif any(ext in lname for ext in ['lat', 'latitude', 'y_coord', 'ycoord']):
                self.LatSelect.v_model = name
                
    def _clear_select(self):
        """clear the select v_model"""
        self.IdSelect.items = [] # all the others are listening to this one 
        self.IdSelect.v_model = self.LngSelect.v_model = self.LatSelect.v_model = None
        
        return 
    
    def _on_select_change(self, change):
        
        name = change['owner']._metadata['name']
        self._set_value(name, change['new'])
        
        return
        
    def _set_value(self, name, value):
        
        """ set the value in the json dictionary"""
        tmp = json.loads(self.v_model)
        tmp[name] = value
        self.v_model = json.dumps(tmp)
        
        return
    
    def get_v_model(self):
        """get the v_model as a dict"""
        return json.loads(self.v_model)
    
    def get_pathname(self):
        """return the pathname from v_model"""
        return json.loads(self.v_model)['pathname']
    
    def get_id_lbl(self):
        """return the id column label from v_model"""
        return json.loads(self.v_model)['id_column']
    
    def get_lng_lbl(self):
        """return the longitude column label from v_model"""
        return json.loads(self.v_model)['lng_column']
    
    def get_lat_lbl(self):
        """return the latitude column label from v_model"""
        return json.loads(self.v_model)['lat_column']
    
    
    class _LocalSelect(v.Select):
            
            def __init__(self, metadata, label):
                
                super().__init__(
                    _metadata = {'name': metadata}, 
                    items     = [], 
                    label     = label, 
                    v_model   = None
                )

class AssetSelect(v.Combobox, SepalWidget):
    
    def __init__(self, label = 'Select an asset', folder = None):
        
        # if folder is not set use the root one 
        self.folder = folder if folder else ee.data.getAssetRoots()[0]['id'] + '/'
        
        # get the list of user asset
        assets = ee.data.listAssets({'parent': self.folder})['assets']
        
        # would be interesting when it will work
        #items = [{'text': asset['name'].replace(self.folder, ''), 'value': asset['name']} for asset in assets]
        items = [asset['name'] for asset in assets]
        
        super().__init__(
            clearable       = True,
            class_          = 'mb-5',
            label           = label,
            placeholder     = 'users/someCustomUser/customAsset',
            hint            = "select an asset in the list or write a custom asset name. Be careful that you need to have access to this asset to use it",
            persistent_hint = True,
            items           = items,
            v_model         = None
        )
        