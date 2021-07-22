import os
from functools import partial
from pathlib import Path
from traitlets import List, Dict, Int, link
import ipyvuetify as v

import sepal_ui.sepalwidgets as sw
from sepal_ui.message import ms

from sepal_ui.scripts.utils import loading_button
from sepal_ui.reclassify.reclassify_widgets import EditTableDialog
from sepal_ui.reclassify.customize_table import ClassTable

class Flex(v.Flex, sw.SepalWidget):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
class ReclassifyView(v.Card):

    def __init__(self, 
                 model,
                 w_reclassify_table, 
                 class_path, 
                 gee=False, 
                 save=True, 
                 *args,
                 **kwargs):
        
        self.class_='pa-2'
        
        super().__init__(*args, **kwargs)
        
        self.model = model
        self.gee = gee
        self.save = save
        self.map_ = None
        self.class_path = class_path
        self.w_reclassify_table = w_reclassify_table
        
        self.dialog = EditTableDialog(self.w_reclassify_table, self.model, class_path)
        self.alert_dialog = sw.Alert()
                
        self.w_class_file = v.Select(
            label=ms.reclassify.class_file_label, 
            v_model='',
            dense=True
        )
        self.get_items()
        
        self.get_table_btn = sw.Btn(
            ms.reclassify.get_table_btn, 
            'mdi-table',
            class_='mb-2',
            outlined=True)
        
        self.reclassify_btn = sw.Btn(
            ms.reclassify.reclassify_btn, 
            'mdi-checkerboard', 
            class_='ml-2 my-2'
        )
                
        self.edit_btn = sw.Btn(
            ms.reclassify.edit_table_btn, 
            'mdi-pencil',
            class_='my-2',
            outlined=True,
        )
        
        self.action_buttons = Flex(class_='d-flex align-center mb-2', children=[
            self.edit_btn, self.reclassify_btn
        ]).hide()
        
        if not self.gee:
            
            # Load reclassify local rasters
            title = v.CardTitle(children=[ms.reclassify.raster.title])
            description = v.CardText(
                class_='py-0', 
                children=[sw.Markdown(ms.reclassify.raster.description)]
            )

            self.w_select_raster = sw.FileInput(
                ['.tif'], label=ms.reclassify.raster.w_select_raster, 
            )

            self.children = [
                    self.dialog,
                    title,
                    description,
                    self.alert_dialog,
                    self.w_select_raster,
                    self.w_class_file,
                    self.get_table_btn,
                    self.action_buttons
            ]
            
            # Capture and bind to model
            self.model.bind(self.w_select_raster, 'in_raster')
            
        else:
            # Load reclassify GEE assets
            title = v.CardTitle(children=[ms.reclassify.gee.title])
            description = v.CardText(
                class_='py-0', 
                children=[sw.Markdown(ms.reclassify.gee.description)]
            )
            
            self.asset_selector = sw.AssetSelect(
                label=ms.reclassify.gee.widgets.asset_label, 
                default_asset=''
            ).show()

            self.w_code = v.Select(label='', class_='pr-4', v_model='')

            self.w_asset = Flex(
                _metadata = {'name':'code'},
                class_='d-flex align-center mb-2',
                children=[self.w_code, self.get_table_btn]
            ).hide()
            
            self.model.bind(self.asset_selector, 'asset_id')\
                        .bind(self.w_code, 'code_col')
            
            self.asset_selector.observe(self.fill_cols, 'v_model')

            self.children = [
                self.dialog,
                title, 
                description, 
                self.alert_dialog,
                self.w_class_file,
                self.asset_selector, 
                self.w_asset,
                self.action_buttons

            ]
            
        # Decorate functions
        self.reclassify = loading_button(
            self.alert_dialog, self.reclassify_btn, debug=True,
        )(self.reclassify)
        
        self.get_reclassify_table = loading_button(
            self.alert_dialog, self.get_table_btn, debug=True
        )(self.get_reclassify_table)

        # Events
        self.get_table_btn.on_event('click', self.get_reclassify_table)
        self.edit_btn.on_event('click', lambda *args: self.dialog.show())

        self.reclassify_btn.on_event('click', partial(self.reclassify, save=self.save))

        
        # Refresh tables        
        self.model.observe(self.get_items, 'classes_files')

    def reclassify(self, *args, save=False):
        """Reclassify the input raster and store it in memory"""
        
        change_matrix = self.w_reclassify_table.matrix

        if self.gee:
            if self.save:
                # Reclassify an gee asset and save it
                task, new_asset_id = self.model.remap_ee_object(
                    band=self.w_code.v_model, 
                    change_matrix=change_matrix,
                    save=save
                )
                self.alert_dialog.add_msg(
                    ms.reclassify.gee.success_export.format(task, new_asset_id), 
                    type_='success'
                )
            else:
                # Reclassify an gee asset and store it in memory
                self.model.remap_ee_object(
                    band=self.w_code.v_model, 
                    change_matrix=change_matrix,
                    save=save
                )
                self.alert_dialog.add_msg(
                    ms.reclassify.gee.success_reclass, type_='success')
            
        else:
            
            # Get reclassify path raster
            filename = Path(self.model.in_raster).stem
            dst_raster = Path(self.model.results_dir)/f'{filename}_reclassified.tif'

            self.model.reclassify_raster(
                change_matrix,
                dst_raster=dst_raster, 
                overwrite=True,
                save=save
            )

            self.alert_dialog.add_msg(
                ms.reclassify.raster.success_reclass.format(dst_raster), type_='success'
            )

    def get_reclassify_table(self, *args):
        """Display a reclassify table which will lead the user to select
        a local code 'from user' to a target code based on a classes file"""
        
        if self.gee:
            if self.model.asset_type == 'IMAGE':
                code_fields = self.model.get_unique_ee()
            elif self.model.asset_type == 'TABLE':
                code_fields = self.model.get_fields()
            else:
                raise(ms.reclassify.gee.wrong_asset)
        else:
            code_fields = self.model.unique()
        
        
        self.w_reclassify_table._get_matrix(code_fields, self.w_class_file.v_model).show()
        
        # Link widget after get the matrix,otherwise it won't work.
        link((self.w_reclassify_table, 'matrix'), (self.model, 'matrix'))
        
        self.dialog.v_model=True
        self.action_buttons.show()
        
    def get_items(self, *args):
        """Get classes .csv files from the selected path"""
        
        self.w_class_file.items = [{'text':ms.reclassify.manual_class, 'value':''}] + \
            [{'divider':True}] + \
            [{'text':Path(f).name, 'value':f} for f 
             in self.model.classes_files]        
        

    def fill_cols(self, *args):
        """Get columns or bands from a featurecollection or an Image"""
        # Hide previous loaded components
        
        self.hide_components()
        
        self.w_code.items=[]
        self.w_asset.show()
        
        self.model.validate_asset()

        self.w_code.loading=True

        # Get columns of dataset
        if self.model.asset_type == 'TABLE':
            self.w_code.label = ms.reclassify.w_code_table
            columns = self.model.get_cols()

        elif self.model.asset_type == 'IMAGE':
            self.w_code.label = ms.reclassify.w_code_image
            columns = self.model.get_bands()

        # Fill widgets with column names
        self.w_code.items = columns
        self.w_code.loading=False
        
    def hide_components(self):
        
        self.dialog.v_mdel=False
        self.action_buttons.hide()
        