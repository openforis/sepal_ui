import os 
from pathlib import Path

import ipyvuetify as v
from traitlets import HasTraits, Unicode, link
from ipywidgets import jslink

from .sepalwidget import SepalWidget
from ..styles.styles import *
from ..scripts import utils as su
from .btn import Btn

class DatePicker(v.Layout, SepalWidget):
    
    def __init__(self, label="Date", **kwargs):
        
        date_picker = v.DatePicker(
            no_title=True, 
            v_model=None, 
            scrollable=True
        )

        date_text =  v.TextField(
            v_model=None,
            label=label,
            hint="YYYY-MM-DD format",
            persistent_hint=True, 
            prepend_icon="event",
            readonly=True,
            v_on='menuData.on'
        )

        menu = v.Menu(
            transition="scale-transition",
            offset_y=True,       
            v_slots=[{
                'name': 'activator',
                'variable': 'menuData',
                'children': date_text,
            }], 
            children=[date_picker]
        )

        super().__init__(
            v_model=None,
            row=True,
            class_='pa-5',
            align_center=True,
            children=[v.Flex(xs10=True, children=[menu])],
            **kwargs
        )

        jslink((date_picker, 'v_model'), (date_text, 'v_model'))
        jslink((date_picker, 'v_model'), (self, 'v_model'))
        
class FileInput(v.Flex, SepalWidget, HasTraits):

    file = Unicode('')
    
    def __init__(self, 
        extentions=[], 
        folder=os.path.expanduser('~'), 
        label='search file', 
        v_model = None,
        **kwargs):

        self.extentions = extentions
        self.folder = folder
        
        self.selected_file = v.TextField(
            label='Selected file', 
            class_='ml-5 mt-5',
            v_model=self.file
        )

        self.loading = v.ProgressLinear(
            indeterminate = False, 
            background_color = 'grey lighten-4',
            color = COMPONENTS['PROGRESS_BAR']['color']
            )
        
        self.file_list = v.List(
            dense=True, 
            color='grey lighten-4',
            flat=True,
            max_height = '300px',
            style_='overflow: auto',
            children=[ 
                v.ListItemGroup(
                    children=self.get_items(),
                    v_model=''
                )
            ]
        )

        self.file_menu = v.Menu(
            min_width=300,
            children=[self.loading, self.file_list], 
            close_on_content_click=False,
            v_slots=[{
                'name': 'activator',
                'variable': 'x',
                'children': Btn(icon='mdi-file-search', v_model=False, v_on='x.on', text=label)
        }])
        
        super().__init__(
            row=True,
            class_='d-flex align-center mb-2',
            align_center=True,
            children=[
                self.file_menu,
                self.selected_file,
            ],
            **kwargs
        )
        
        link((self.selected_file, 'v_model'), (self, 'file'))
        link((self.selected_file, 'v_model'), (self, 'v_model'))

        def on_file_select(change):
            new_value = change['new']
            if new_value:
                if os.path.isdir(new_value):
                    self.folder = new_value
                    self.change_folder()
                
                elif os.path.isfile(new_value):
                    self.file = new_value

        self.file_list.children[0].observe(on_file_select, 'v_model')
                
    def change_folder(self):
        """change the target folder"""
        #reset files
        self.file_list.children[0].children = self.get_items()
    

    def get_items(self):
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
    
    def get_parent_path(self):
        """return the list of all the parents of a given path"""
        path_list = [self.folder]
        path = Path(self.folder)

        while  str(path.parent) != path_list[-1]:
            path = path.parent
            path_list.append(str(path))
        
        return path_list