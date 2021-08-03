from pathlib import Path
from traitlets import List, Dict, Int, link

import ipyvuetify as v
import ee

import sepal_ui.sepalwidgets as sw
from sepal_ui.message import ms
from sepal_ui.scripts.utils import loading_button
from .reclassify_model import ReclassifyModel
        
class ComboSelect(v.Select, sw.SepalWidget):
    """
    Custom select to pick values from the input classification. They can be linked to each other to adapt their list of items according to what have already been selected/deselected. 
    
    Args:
        new_code (int): the code of the new class 
        codes (list(int)): the complete list of values available in the inputs
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
        Synchronise all the combo select so that any value that is already selected cannot be reselected. Using the same process, once a value is freed elswhere, it is repopulated in every ComboSelect.
        
        Args:
            combo_list (list): the list of the other COmboSelect that share the same list of items
        
        Return:
            self
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
        diff = list(set(change['old']).symmetric_difference(change['new']))[0] # I assume that there is only one change
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
    2 columns are integrated, the new class value and the values in the original input
    One can select multiple class to be reclassify in the new classification
    
    Args:
        model (ReclassifyModel): model embeding the traitlet dict to store the reclassifying matrix. keys: class value in dst, values: list of values in src.
        dst_classes (dict|optional): a dictionnary that represent the classes of new the new classification table as {class_code: class_name}. class_code must be ints and class_name str.
        src_classes (list|optional): the list of existing values within the input file
        
    Attributes:
        HEADER (list): name of the column header (to, from)
        model (ReclassifyModel): the reclassifyModel object to manipulate the input file and save parameters
    """
    
    HEADERS = ms.rec.rec.headers
    
    def __init__(self, model, dst_classes={}, src_classes=[], **kwargs):
        
        # create the table 
        super().__init__(**kwargs)
        
        # save the model 
        self.model = model
        
        # create the table elements
        self._header = [v.Html(tag='tr', children=[v.Html(tag = 'th', children = [h]) for h in self.HEADERS])]
        self.set_table(dst_classes, src_classes)
        
        
    def set_table(self, dst_classes, src_classes):
        """
        Rebuild the table content based on the new_classes and codes provided
        
        Args:
            dst_classes (dict|optional): a dictionnary that represent the classes of new the new classification table as {class_code: class_name}. class_code must be ints and class_name str.
            src_classes (list|optional): the list of existing values within the asset/raster
            
        Return:
            self
        """
        
        # reset the matrix
        self.model.matrix = {code: [] for code in dst_classes.keys()}
        
        # create the select list
        # they need to observe each other to adapt the available class list dynamically 
        self.combos  = {k: ComboSelect(k, src_classes) for k in dst_classes.keys()}
        for combo in self.combos.values(): 
            combo.link_combos(self.combos)
            combo.observe(self._update_matrix_values, 'v_model')
        
        rows = [
            v.Html(tag='tr', children=[
                v.Html(tag='td', children=[str(name)]), 
                v.Html(tag='td', children=[self.combos[code]])
            ]) for code, name in dst_classes.items()
        ]
        
        # add an empty row at the end to make the table more visible when it's empty 
        rows += [v.Html(tag='tr', children=[
            v.Html(tag='td', children=['']),
            v.Html(tag='td', children=['' if len(dst_classes) else 'No data available'])
        ])]
        
        self.children = [v.Html(tag='tbody', children= self._header + rows)]
        
        return self
    
    def _update_matrix_values(self, change):
        """Update the appropriate matrix value when a Combo select change"""
        
        # get the code of the class in the dst classification
        code = change['owner']._metadata['class']
        
        # bind it to classes in the src classification
        self.model.matrix[code] = change['new']
        
        return self
        
class ReclassifyView(v.Card):
    """
    Stand-alone Card object allowing the user to reclassify a input file. the input can be of any type (vector or raster) and from any source (local or GEE). 
    The user need to provide a destination classification file (table) in the following format : 3 headless columns: 'code', 'desc', 'color'. Once all the old class have been attributed to their new class the file can be exported in the source format to local memory or GEE. the output is also savec in memory for further use in the app. It can be used as a tile in a sepal_ui app. The id_ of the tile is set to "reclassify_tile"
    
    Args:
        model (ReclassifyModel): the reclassify model to manipulate the classification dataset. default to a new one
        class_path (str|optional): Folder path containing already existing classes. Default to ~/
        out_path (str|optional): the folder to save the created classifications. default to ~/downloads
        gee (bool): either or not to set :code:`gee` to True. default to False
        
    Attributes:
        model (ReclassifyModel): the reclassify model to manipulate the classification dataset
        gee (bool): either being linked to gee or not (use local file or GEE asset for the rest of the app)
        alert (sw.Alert): the alert to display informations about computation
        title (v.Cardtitle): the title of the card
        w_asset (sw.AssetSelect): the widget to select an asset input 
        w_raster (sw.FileInput): the widget to select a file input
        w_image (Any): wraper of the input. linked to w_asset if gee=True, else to w_raster
        w_band (int|str): widget to select the band/property used as init classification in the input file
        get_table_btn (sw.Btn): the btn to load the data in the reclassification table
        w_class_file (sw.FileInput): widget to select the new classification system file (3 headless columns: 'code', 'desc', 'color')
        reclassify_table (ReclassifyTable): the reclassification table populated via the previous widgets
        reclassify_btn (sw.Btn): the btn to launch the reclassifying process
    """

    def __init__(self, model=None, class_path=Path.home(), out_path=Path.home()/'downloads', gee=False, **kwargs):
        
        # create metadata to make it compatible with the framwork app system
        self._metadata = {'mount_id':'reclassify_tile'}
        
        # init card parameters
        self.class_='pa-5'
        
        # create the object
        super().__init__(**kwargs)
        
        # set up a default model 
        self.model = model if model else ReclassifyModel(gee=gee, dst_dir=out_path)
        
        # set the folders
        self.class_path = Path(class_path)
        self.out_path = Path(out_path)
        
        # save the gee binding
        self.gee = gee
        if gee: ee.Initialize() 
        
        # create an alert to display information to the user
        self.alert = sw.Alert()
                
        # create the widgets
        self.title = v.CardTitle(children=[v.Html(tag='h2', children=[ms.rec.rec.title])])
        
        w_input_title = v.Html(tag='h2', children=[ms.rec.rec.input.title], class_='mt-2')
        self.w_asset = sw.AssetSelect(label=ms.rec.rec.input.asset)
        self.w_raster = sw.FileInput(['.tif', '.vrt', '.tiff', '.geojson', '.shp'], label=ms.rec.rec.input.file)
        self.w_image = self.w_asset if self.gee else self.w_raster
        self.w_band = v.Select(label=ms.rec.rec.input.band.label, hint=ms.rec.rec.input.band.hint, v_model = None, items=[], persistent_hint=True)
        
        w_class_title = v.Html(tag='h2', children=[ms.rec.rec.input.classif.title], class_='mt-2')
        self.w_class_file = sw.FileInput(['.csv'], label=ms.rec.rec.input.classif.label, folder=self.class_path)
        
        self.get_table_btn = sw.Btn(ms.rec.rec.input.btn, 'mdi-table',class_='ma-5', color='success', outlined=True)
        
        w_table_title = v.Html(tag='h2', children=[ms.rec.rec.table], class_='mt-2')
        self.reclassify_table = ReclassifyTable(self.model)
        
        self.reclassify_btn = sw.Btn(ms.rec.rec.btn, 'mdi-checkerboard', disabled=True)
        
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
            w_input_title, self.w_image, self.w_band,
            w_class_title, self.w_class_file,
            self.get_table_btn,
            self.alert,
            w_table_title, self.reclassify_table,
            self.reclassify_btn
        ]
             
        # Decorate functions
        self.reclassify = loading_button(self.alert, self.reclassify_btn, debug=True)(self.reclassify)
        self.get_reclassify_table = loading_button(self.alert, self.get_table_btn, debug=True)(self.get_reclassify_table)

        # JS Events
        self.w_image.observe(self._update_band, 'v_model')
        self.get_table_btn.on_event('click', self.get_reclassify_table)
        self.reclassify_btn.on_event('click', self.reclassify)

    def reclassify(self, widget, event, data):
        """
        Reclassify the input and store it in the appropriate format.
        The input is not saved locally to avoid memory overload.
        
        Return:
            self
        """
        
        # create the output file 
        self.model.reclassify()
            
        return self

    def _update_band(self, change):
        """Update the band possibility to the available bands/properties of the input"""
        
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
        
        Return:
            self
        """
        
        # check that everything is set 
        if not self.w_image.v_model: raise AttributeError('missing image')
        if not self.w_band.v_model: raise AttributeError('missing band')
        if not self.w_class_file.v_model: raise AttributeError('missing file')
            
        # get the destination classes
        dst_classes = self.model.get_dst_classes()
        
        # get the src_classes
        src_classes = self.model.unique()
        
        # reset the table 
        self.reclassify_table.set_table(dst_classes, src_classes)
        
        # enable the reclassify btn 
        self.reclassify_btn.disabled = False
        
        return self
    
    def nest_tile(self):
        """
        Prepare the view to be used as a nested component in a tile. 
        the elevation will be set to 0 and the title remove from children.
        The mount_id will also be changed to nested
        
        Return:
            self
        """
        
        # remove id 
        self._metadata['mount_id'] = 'nested_tile'
        
        # remove elevation 
        self.elevation =  False
        
        # remove title 
        without_title = self.children.copy()
        without_title.remove(self.title)
        self.children = without_title
        
        return self
        