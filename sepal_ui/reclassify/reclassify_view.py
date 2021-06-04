import os
from functools import partial
from pathlib import Path
from traitlets import List, Dict, Int
import ipyvuetify as v

import sepal_ui.sepalwidgets as sw
from sepal_ui.message import ms

from sepal_ui.scripts.utils import loading_button
from sepal_ui.reclassify.customize_table import ClassTable
from sepal_ui.reclassify.reclassify_model import ReclassifyModel

class Flex(v.Flex, sw.SepalWidget):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
class ReclassifyView(v.Card):

    def __init__(self, w_reclassify_table, class_path, gee=False, *args, **kwargs):

        super().__init__(*args, **kwargs)
        
        self.model = ReclassifyModel()
        self.class_path = class_path
        self.w_reclassify_table = w_reclassify_table
        
        self.alert_dialog = sw.Alert().hide()
        
        self.customize_view = CustomizeView(self.class_path)
        
        self.w_class_file = v.Select(
            label='Select a classes file', 
            v_model='',
            dense=True
        )
        self.get_items()
        
        self.get_table_btn = sw.Btn('Get reclassify table', class_='mb-2')
        self.save_raster_btn = sw.Btn('Reclassify', class_='my-2').hide()
        
        if not gee:
            
            # Load reclassify local rasters
            title = v.CardTitle(children=[ms.reclassify.title])
            description = v.CardText(
                class_='py-0', 
                children=[sw.Markdown(ms.reclassify.description)]
            )

            self.w_select_raster = sw.FileInput(
                ['.tif'], label='Search raster'
            )

            self.children = [
                    title,
                    description,
                    self.w_select_raster,
                    self.w_class_file,
                    self.get_table_btn,
                    self.w_reclassify_table,
                    self.save_raster_btn,
                    self.alert_dialog,
            ]
            
            # Capture and bind to model
            self.model.bind(self.w_select_raster, 'in_raster')
            
        else:
            # Load reclassify GEE assets
            title = v.CardTitle(children=[ms.reclassify.title])
            description = v.CardText(
                class_='py-0', 
                children=[sw.Markdown(ms.reclassify.description)]
            )
            
            self.asset_selector = sw.AssetSelect(
                label='cm.remap.label', 
                default_asset = 'users/dafguerrerom/FAO/LULC_2012_AOI'
            ).show()

            self.w_code = v.Select(label='', class_='pr-4', v_model='')
            self.mapper_btn = sw.Btn('cm.remap.btn', small=True)

            self.w_asset = Flex(
                _metadata = {'name':'code'},
                class_='d-flex align-center mb-2',
                children=[self.w_code, self.mapper_btn]
            ).hide()
            
            self.model.bind(self.asset_selector, 'asset_id')
            
            self.asset_selector.observe(self.fill_cols, 'v_model')

            self.children = [
                title, 
                description, 
                self.asset_selector, 
                self.w_asset
            ]
            
        # Decorate functions
        self.reclassify_and_save = loading_button(
            self.alert_dialog, self.save_raster_btn, debug=True,
        )(self.reclassify_and_save)

        self.get_reclassify_table = loading_button(
            self.alert_dialog, self.get_table_btn, debug=True
        )(self.get_reclassify_table)

        # Events
        self.get_table_btn.on_event('click', self.get_reclassify_table)
        self.save_raster_btn.on_event('click', self.reclassify_and_save)

        # Refresh tables        
        self.customize_view.observe(self.get_items, 'classes_files')

    def get_reclassify_table(self, *args):
        """Display a reclassify table which will lead the user to select
        a local code 'from user' to a target code based on a classes file"""
        
        code_fields = self.model.unique()
        self.w_reclassify_table._get_matrix(code_fields, self.w_class_file.v_model)
        self.save_raster_btn.show()
        
    def get_items(self, *args):
        """Get classes .csv files from the selected path"""
        
        self.w_class_file.items = [{'text':'Manual classification', 'value':''}] + \
            [{'divider':True}] + \
            [{'text':Path(f).name, 'value':f} for f 
             in self.customize_view.classes_files]
        
    def reclassify_and_save(self, *args):
        """Reclassify the input raster and save it in sepal space"""
        
        change_matrix = self.w_reclassify_table.matrix
        
        map_values = {
            k: v['value'] if 'text' in v else v
                for k, v in change_matrix.items()
        }
            # Get reclassify path raster
        filename = Path(self.model.in_raster).stem
        dst_raster = Path('~').expanduser()/f'downloads/{filename}_reclassified.tif'
        
        self.model.reclassify_from_map(
            map_values, dst_raster=dst_raster, overwrite=True
        )
        
        self.alert_dialog.add_msg(
            'File {} succesfully reclassified'.format(dst_raster), type_='success'
        )
        
    def fill_cols(self, *args):
        """Get columns or bands from a featurecollection or an Image"""
        # Hide previous loaded components
#         self._hide_components()
        
        self.w_code.items=[]
        self.w_asset.show()
        
        self.model.validate_asset()

        self.w_code.loading=True

        # Get columns of dataset
        if self.model.asset_type == 'TABLE':
            self.w_code.label = "cm.remap.code_label"
            columns = self.model.get_cols()

        elif self.model.asset_type == 'IMAGE':
            self.w_code.label = "cm.remap.band_label"
            columns = self.model.get_bands()

        # Fill widgets with column names
        self.w_code.items = columns

        self.w_code.loading=False
    

class CustomizeView(v.Card):
    
    classes_files = List([]).tag(sync=True)
    
    def __init__(
        self, 
        class_path, 
        *args, **kwargs):
        
        """Stand-alone tile composed by a select widget containing 
        .csv reclassify files found in the class_path, and a ClassTable 
        to edit and/or create a new classification table,
        
        Args:
            class_path (str) (optional): Folder path containing 
            classification tables
        """
        
        super().__init__(*args, **kwargs)
        
        self.title = v.CardTitle(children=['Edit or create new classifications'])
        self.class_path = class_path
        
        alert = sw.Alert()
        
        self.w_class_file = v.Select(
            label='Select a classes file', 
            items=self.get_items(), 
            v_model='',
            dense=True
        )
        self.class_table = ClassTable(
            out_path=self.class_path,
            schema = {'id':'number', 'code':'number', 'description':'string'},
        ).hide()

        use_btn = sw.Btn('Get table')
        self.children=[
            self.title,
            v.Flex(class_='ml-2 d-flex', children=[
                self.w_class_file,
                use_btn,
            ]),
            alert,
            self.class_table
        ]
        self.get_classes_files()
        
        # Decorate functions
        self.get_class_table = loading_button(
            alert, use_btn
        )(self.get_class_table)
        
        # Events
        
        # Listen Class table save dialog to refresh the classes widget
        self.class_table.save_dialog.observe(self._refresh_files, 'reload')
        
        # Get the corresponding table
        use_btn.on_event('click', self.get_class_table)
        
    def get_class_table(self, *args):
        """Display class table widget in view"""

        # Call class table method to build items
        self.class_table.populate_table(self.w_class_file.v_model)
        self.class_table.show()
                
    def _refresh_files(self, *args):
        """Trigger event when a new file is created"""
        self.get_classes_files()
        self.w_class_file.items = self.get_items()
        
    def get_classes_files(self):
        """Search for classes inside module path"""

        look_up_folder = Path(self.class_path).glob('*.csv')
        module_classes_folder = (Path(os.getcwd())/'component/parameter').glob('*.csv')
        
        self.classes_files = [str(f) for f in (list(look_up_folder) + \
                                               list(module_classes_folder))]
    
    def get_items(self):
        """Get items for widget selection"""
        self.get_classes_files()
        classes_files = [{'divider':True}, {'header':'New classification'}] + \
                        [{'text':'Create new classification...', 'value':''}] + \
                        [{'divider':True}, {'header':'Local classifications'}] + \
                        [{'text':Path(f).name, 'value':f}  for f in self.classes_files]

        return classes_files
    

# class ReclassifyGee(v.Card):
    
#         self.w_class_file = class_file
        
#         super().__init__(*args, **kwargs)

#         self.ee_asset = None
#         self.w_reclassify = ReclassifyTable(
#             dense=True, 
#             max_height=400,
#             _metadata={'name':'mapper'}
#         ).hide()
        

        
#         # List of components whose could be hidden/showed
        
#         self.components = {
#             'mapper': self.w_reclassify,
#             'code' : self.w_asset
#         }
        
#         # Define view
#         self.children = [
#             self.asset_selector,
#             self.w_reclassify,
            
#         ]
        
#         #Link traits
#         link((self, 'asset'), (self.asset_selector, 'v_model'))
#         link((self.w_code, 'v_model'), (self, 'code_col'))
        
#         # Decorate functions
#         self._get_mapper_matrix = loading(
#             self.alert_dialog, 
#             self.mapper_btn)(self._get_mapper_matrix)
        
#         self._validate_asset = loading(
#             self.alert_dialog)(self._validate_asset)
        
#         # Trigger events
#         self.mapper_btn.on_event('click', self._get_mapper_matrix_event)

#     def _get_mapper_matrix_event(self, widget, event, data):
#         self._get_mapper_matrix()
        
#     def _get_mapper_matrix(self):
        
#         assert (self.code_col != ''), cm.remap.error.no_code_col
        
#         if self.asset_type == 'TABLE':
#             code_fields = self._get_fields()
#         elif self.asset_type == 'IMAGE':
#             code_fields = self._get_classes()
        
#         # Create mapper widget
#         self.w_reclassify._get_matrix(self.w_class_file.v_model, code_fields)
#         self.w_reclassify.show()

#     def _hide_components(self):
#         """Hide all possible componentes"""
#         self.code_col = ''
#         for component in self.components.values():
#             su.hide_component(component)
    
