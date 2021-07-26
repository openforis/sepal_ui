import os
from functools import partial
from pathlib import Path
from traitlets import List, Dict, Int, link
import ipyvuetify as v
import ee

import sepal_ui.sepalwidgets as sw
from sepal_ui.message import ms

from sepal_ui.scripts.utils import loading_button
from sepal_ui.reclassify.reclassify_model import ReclassifyModel
from sepal_ui.reclassify.reclassify_widgets import EditTableDialog, ReclassifyTable
        
class ComboSelect(v.Select, sw.SepalWidget):
    """
    Custom select to pick values from the initial raster. They can be linked to each other to adapt their list of items according to what have already been selected
    
    Args:
        new_code (int): the code of the new class 
        codes (list(int)): the complete list of values available in the raster
    """
    
    def __init__(self, new_code, codes, **kwargs):
        
        # set default parameters
        self.dense = True
        self.multiple = True
        self.chips = True
        self.deletable_chips = True
        self._metadata = {'class': new_code}
        self.v_model = []
        
        # init the select
        super().__init__(**kwargs)
        
        # set the initial codes list 
        self.items = codes
        
    def link_combos(self, combo_list):
        """
        Synchronise all the combo select so that any value that is already selected cannot be reselected
        """
        
        # remove self from the combo list
        combos = [c for c in combo_list.values() if c != self]
        
        # apply the observe method on every one of them 
        for combo in combos: 
            combo.observe(self._update_items, 'v_model')
            
        return self
        
    def _update_items(self, change):
        """change the item list based on the change in another combo"""
        
        # extract the dif between the 2 lists
        diff = list(set(change['old']).symmetric_difference(change['new']))[0] # I assume that there is only one
        remove = len(change['old']) > len(change['new'])
        
        # adapt the item list 
        init_items = self.items.copy()
        if remove: 
            self.items = sorted(init_items + [diff])
        else:
            self.items = [i for i in init_items if i != diff]
            
        return self
    
class ReclassifyTable(v.SimpleTable, sw.SepalWidget):
    """
    Table to store the reclassifying information. 
    2 columns are integrated, the new class value and the value in the original asset/raster
    One can select multiple class to be reclassify in the new classification
    
    Args:
        model (ReclassifyModel): model embeding the traitlet dict to store the reclassifying matrix. keys: class value in dst, values: list of values in src.
        dst_classes (dict|optional): a dictionnary that represent the classes of new the new classification table as {class_code: class_name}. class_code must be ints and class_name str.
        src_classes (list|optional): the list of existing values within the asset/raster
    """
    
    HEADERS = ['To: Custom Code', 'From: user code']
    
    def __init__(self, model, dst_classes={}, src_classes=[], **kwargs):
        
        # create the table 
        super().__init__(**kwargs)
        
        # save the model 
        self.model = model
        
        # create the table elements
        self.header = [v.Html(tag='tr', children=[v.Html(tag = 'th', children = [h]) for h in self.HEADERS])]
        self.set_table(dst_classes, src_classes)
        
        
    def set_table(self, dst_classes, src_classes):
        """
        rebuild the table content based on the new_classes and codes provided
        
        Args:
            dst_classes (dict|optional): a dictionnary that represent the classes of new the new classification table as {class_code: class_name}. class_code must be ints and class_name str.
            src_classes (list|optional): the list of existing values within the asset/raster
        """
        
        # reset the matrix
        self.model.matrix = {code: [] for code in dst_classes.keys()}
        
        # create the select list
        # they need to observe each other to adapt the available class list dynamically 
        self.combos  = {k: ComboSelect(k, src_classes) for k in dst_classes.keys()}
        for combo in self.combos.values(): 
            combo.link_combos(self.combos)
            combo.observe(self._update_matrix_values, 'v_model')
            
        print(dst_classes)
        
        rows = [
            v.Html(tag='tr', children=[
                v.Html(tag='td', children=[str(name)]), 
                v.Html(tag='td', children=[self.combos[code]])
            ]) for code, name in dst_classes.items()
        ]
        
        self.children = [v.Html(tag='tbody', children= self.header + rows)]
        
        return self
    
    def _update_matrix_values(self, change):
        """update the appropriate matrix value when a Combo select change"""
        
        # get the code of the class in the dst classification
        code = change['owner']._metadata['class']
        
        # bind it to classes in the src classification
        self.model.matrix[code] = change['new']
        
        return self
        
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
        self.w_raster = sw.FileInput(['.tif', '.vrt', '.tiff', '.geojson', '.shp'], label=ms.reclassify.class_file_label, folder=self.folder)
        self.w_image = self.w_asset if self.gee else self.w_raster
        self.w_band = v.Select(label="Select band", hint="The band to use or the vector feature", v_model = None, items=[], persistent_hint=True)
        
        self.get_table_btn = sw.Btn(ms.reclassify.get_table_btn, 'mdi-table',class_='ma-5', color='success')
        
        self.w_class_file = sw.FileInput(['.csv'], label="Select classification system", folder=self.folder)
        action_image = v.Flex(class_="d-flex", children=[self.w_image, self.get_table_btn])
        
        self.reclassify_table = ReclassifyTable(self.model)
        
        self.reclassify_btn = sw.Btn(ms.reclassify.reclassify_btn, 'mdi-checkerboard', class_='ml-2 my-2',disabled=True)
        
        # bind to the model
        # bind to the 2 raster and asset as they cannot be displayed at the same time
        self.model \
            .bind(self.w_raster, 'src_local') \
            .bind(self.w_asset, 'src_gee') \
            .bind(self.w_band, 'band') \
            .bind(self.w_class_file, 'dst_class_file')

        # create the layout
        self.children = [
            self.title,
            self.alert,
            self.w_image, 
            self.w_band,
            self.w_class_file,
            self.get_table_btn,
            self.reclassify_table,
            self.reclassify_btn
        ]
             
        # Decorate functions
        self.reclassify = loading_button(self.alert, self.reclassify_btn, debug=True)(self.reclassify)
        self.get_reclassify_table = loading_button(self.alert, self.get_table_btn, debug=True)(self.get_reclassify_table)

        # Events
        self.w_image.observe(self._update_band, 'v_model')
        self.get_table_btn.on_event('click', self.get_reclassify_table)
        self.reclassify_btn.on_event('click', self.reclassify)

    def reclassify(self, *args, save=False):
        """
        Reclassify the input and store it in the appropriate format.
        We don't store the input locally to avoid memory overload.
        """
        
        # create the output file 
        self.model.reclassify()
            
        return self
        
        
    #    
    #    change_matrix = self.w_reclassify_table.matrix
#
    #    if self.gee:
    #        if self.save:
    #            # Reclassify an gee asset and save it
    #            task, new_asset_id = self.model.remap_ee_object(
    #                band=self.w_code.v_model, 
    #                change_matrix=change_matrix,
    #                save=save
    #            )
    #            self.alert_dialog.add_msg(
    #                ms.reclassify.gee.success_export.format(task, new_asset_id), 
    #                type_='success'
    #            )
    #        else:
    #            # Reclassify an gee asset and store it in memory
    #            self.model.remap_ee_object(
    #                band=self.w_code.v_model, 
    #                change_matrix=change_matrix,
    #                save=save
    #            )
    #            self.alert_dialog.add_msg(
    #                ms.reclassify.gee.success_reclass, type_='success')
    #        
    #    else:
    #        
    #        # Get reclassify path raster
    #        filename = Path(self.model.in_raster).stem
    #        dst_raster = Path(self.model.results_dir)/f'{filename}_reclassified.tif'
#
    #        self.model.reclassify_raster(
    #            change_matrix,
    #            dst_raster=dst_raster, 
    #            overwrite=True,
    #            save=save
    #        )
#
    #        self.alert_dialog.add_msg(
    #            ms.reclassify.raster.success_reclass.format(dst_raster), type_='success'
    #        )
        return self

    def _update_band(self, change):
        """
        Update the band possibility to the availabel band of the raster/asset
        """
        
        # guess the file type and save it in the model 
        self.model.get_type()
        
        # update the bands values
        self.w_band.v_model = None
        self.w_band.items = self.model.get_bands()
        
        return self
    
    def get_reclassify_table(self, widget, event, data):
        """
        Display a reclassify table which will lead the user to select
        a local code 'from user' to a target code based on a classes file
        """
        
        # check that everythin is set 
        if not self.w_image.v_model: raise Exception('missing image')
        if not self.w_band.v_model: raise Exception('missing band')
        if not self.w_class_file.v_model: raise Exception('missing file')
            
        # get the destination classes
        dst_classes = self.model.get_dst_classes()
        
        # get the src_classes
        src_classes = self.model.unique()
        
        # reset the table 
        self.reclassify_table.set_table(dst_classes, src_classes)
        
        # enable the reclassify btn 
        self.reclassify_btn.disabled = False
        
        return self
        
    #def fill_cols(self, *args):
    #    """Get columns or bands from a featurecollection or an Image"""
    #    # Hide previous loaded components
    #    
    #    self.hide_components()
    #    
    #    self.w_code.items=[]
    #    self.w_asset.show()
    #    
    #    self.model.validate_asset()
#
    #    self.w_code.loading=True
#
    #    # Get columns of dataset
    #    if self.model.asset_type == 'TABLE':
    #        self.w_code.label = ms.reclassify.w_code_table
    #        columns = self.model.get_cols()
#
    #    elif self.model.asset_type == 'IMAGE':
    #        self.w_code.label = ms.reclassify.w_code_image
    #        columns = self.model.get_bands()
#
    #    # Fill widgets with column names
    #    self.w_code.items = columns
    #    self.w_code.loading=False
    #    
    #def hide_components(self):
    #    
    #    self.dialog.v_mdel=False
    #    self.action_buttons.hide()
        