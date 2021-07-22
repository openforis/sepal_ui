import os
from functools import partial
from pathlib import Path
from traitlets import List, Dict, Int, link
import ipyvuetify as v

import sepal_ui.sepalwidgets as sw
from sepal_ui.message import ms

from sepal_ui.scripts.utils import loading_button
from sepal_ui.reclassify.reclassify_model import ReclassifyModel
from sepal_ui.reclassify.reclassify_widgets import EditTableDialog, ReclassifyTable

class Flex(v.Flex, sw.SepalWidget):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
class ReclassifyView(v.Card):

    def __init__(self, folder=None, gee=False, save=True, **kwargs):
        
        self.class_='pa-2'
        
        super().__init__(**kwargs)
        
        # create a default model 
        self.model = ReclassifyModel(gee=gee)
        
        # save the object parameters 
        self.save = save # rember if the reclassify asset needs to be saved
        self.folder = Path(folder) if folder else Path.home() # save rasters in a specific folder
        self.gee = gee
        if gee: ee.Initialize() # save the gee binding
        
        # create an alert to display information to the user
        self.alert = sw.Alert()
                
        # create the widgets
        self.title = v.CardTitle(children=['Reclassify image'])
            
        self.w_asset = sw.AssetSelect(label=ms.reclassify.gee.widgets.asset_label)
        self.w_raster = sw.FileInput(['.tif'], label=ms.reclassify.class_file_label, folder=self.folder)
        self.w_image = self.w_asset if self.gee else self.w_raster
        
        self.get_table_btn = sw.Btn(ms.reclassify.get_table_btn, 'mdi-table',class_='ma-5', color='success')
        action_image = Flex(class_="d-flex", children=[self.w_image, self.get_table_btn])
        self.edit_btn = sw.Btn(ms.reclassify.edit_table_btn, 'mdi-pencil', class_='my-2', outlined=True)
        self.reclassify_btn = sw.Btn(ms.reclassify.reclassify_btn, 'mdi-checkerboard', class_='ml-2 my-2')        
        
        self.action_buttons = Flex(class_='d-flex align-center mb-2', children=[
            self.edit_btn, self.reclassify_btn
        ]).hide()
         
        self.dialog = EditTableDialog(self.model, self.folder) # the dialog to edit the correspondance table
        
        # bind to the model 
        # bind to the 2 raaster and asset as they cannot be displayed at the same time
        self.model.bind(self.w_raster, 'in_raster').bind(self.w_asset, 'asset_id')

        # create the layout
        self.children = [
            self.dialog,
            self.title,
            self.alert,
            action_image,
            self.action_buttons
        ]
             
        # Decorate functions
        self.reclassify = loading_button(self.alert, self.reclassify_btn, debug=True)(self.reclassify)
        self.get_reclassify_table = loading_button(self.alert, self.get_table_btn, debug=True)(self.get_reclassify_table)

        # Events
        self.get_table_btn.on_event('click', self.get_reclassify_table)
        self.edit_btn.on_event('click', lambda *args: self.dialog.show())
        self.reclassify_btn.on_event('click', partial(self.reclassify, save=self.save))

        # Refresh tables        
        #self.model.observe(self.get_items, 'classes_files')

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

    def get_reclassify_table(self, widget, event, data):
        """Display a reclassify table which will lead the user to select
        a local code 'from user' to a target code based on a classes file"""
        
        code_fields = self.model.unique()
        
        self.dialog.reclassify_table._get_matrix(code_fields).show()
        
        # Link widget after get the matrix,otherwise it won't work.
        link((self.dialog.reclassify_table, 'matrix'), (self.model, 'matrix'))
        
        self.dialog.v_model=True
        self.action_buttons.show()  
        
        return self
        
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
        