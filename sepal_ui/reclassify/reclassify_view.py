from pathlib import Path
from traitlets import List, Dict, Int, link

import ipyvuetify as v
import ee

import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import utils as su
from sepal_ui.message import ms
from sepal_ui.scripts.utils import loading_button
from .reclassify_model import ReclassifyModel

class SaveMatrixDialog(v.Dialog):
    """
    Dialog to setup the name of the output matrix file 
    
    Args:
        folder (pathlike object): the path to the save folder. default to ~/
    """
    
    def __init__(self, folder=Path.home(), **kwargs):
        
        # save the matrix 
        self._matrix = {}
        self.folder = Path(folder)
        
        # create the widgets
        title = v.CardTitle(children=["Save matrix"])
        self.w_file = v.TextField(label='filename', v_model=None)
        btn = sw.Btn('Save matrix')
        cancel = sw.Btn('Cancel', outlined=True)
        actions = v.CardActions(children=[cancel, btn])
        
        # default parameters 
        self.value=False
        self.max_width=500
        self.overlay_opcity=0.7
        self.persistent=True
        self.children = [v.Card(
            class_='pa-4',
            children=[title, self.w_file, actions]
        )]
        
        # create the dialog
        super().__init__()
        
        # js behaviour
        cancel.on_event('click', self._cancel)
        btn.on_event('click', self._save)
        self.w_file.on_event('blur', self._sanitize)
        
    def _cancel(self, widget, event, data):
        """do nothing and exit"""
        
        self.w_file.v_model = None
        self.value = False
        
        return self
        
    def _save(self, widget, event, data):
        """save the matrix in a specified file"""
        
        file = self.folder/f'{su.normalize_str(self.w_file.v_model)}.csv'
        
        lines = [f'{src},{dst}' for src, dst in self._matrix.items()]
        file.write_text('\n'.join(lines))
        
        # hide the dialog
        self.value = False
        
        return self
    
    def show(self, matrix):
        """show the dialog and set the matrix values"""
        
        self._matrix = matrix
        self.value = True
        
        return self
    
    def _sanitize(self, widget, event, data):
        """sanitize the used name when saving"""
        
        self.w_file.v_model = su.normalize_str(self.w_file.v_model)
        
        return self
    
class ClassSelect(v.Select, sw.SepalWidget):
    """
    Custom widget to pick the value of a original class in the new classification system
    
    Args:
        new_codes(dict): the dict of the new codes to use as items {code: name}
        code (int): the orginal code of the class
    """
    
    def __init__(self, new_codes, old_code, **kwargs):
        
        print(new_codes)
        
        # set default parameters
        self.items = [{'text': f'{code}: {name}', 'value': code} for code, name in new_codes.items()]
        self.dense = True
        self.multiple = False
        self.chips = True
        self._metadata = {'class': old_code}
        self.v_model = None
        
        # init the select 
        super().__init__(**kwargs)
    
class ReclassifyTable(v.SimpleTable, sw.SepalWidget):
    """
    Table to store the reclassifying information. 
    2 columns are integrated, the new class value and the values in the original input
    One can select multiple class to be reclassify in the new classification
    
    Args:
        model (ReclassifyModel): model embeding the traitlet dict to store the reclassifying matrix. keys: class value in dst, values: list of values in src.
        dst_classes (dict|optional): a dictionnary that represent the classes of new the new classification table as {class_code: class_name}. class_code must be ints and class_name str.
        src_classes (dict|optional): the list of existing values within the input file {class_code: class_name}
        
    Attributes:
        HEADER (list): name of the column header (from, to)
        model (ReclassifyModel): the reclassifyModel object to manipulate the input file and save parameters
    """
    
    HEADERS = ms.rec.rec.headers
    
    def __init__(self, model, dst_classes={}, src_classes={}, **kwargs):
        
        # default parameters 
        self.dense = True
        
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
            src_classes (dict|optional): the list of existing values within the input file {class_code: class_name}
            
        Return:
            self
        """
        
        # reset the matrix
        self.model.matrix = {code: None for code in src_classes.keys()}
        
        # create the select list
        # they need to observe each other to adapt the available class list dynamically 
        self.class_select_list = {k: ClassSelect(dst_classes, k) for k in src_classes.keys()}
        
        rows = [
            v.Html(tag='tr', children=[
                v.Html(tag='td', children=[f'{code}: {name}']), 
                v.Html(tag='td', children=[self.class_select_list[code]])
            ]) for code, name in src_classes.items()
        ]
        
        # add an empty row at the end to make the table more visible when it's empty 
        rows += [v.Html(tag='tr', children=[
            v.Html(tag='td', children=['']),
            v.Html(tag='td', children=['' if len(dst_classes) else 'No data available'])
        ])]
        
        self.children = [v.Html(tag='tbody', children= self._header + rows)]
        
        # js behaviour
        [w.observe(self._update_matrix_values, 'v_model') for w in self.class_select_list.values()]
        
        return self
    
    def _update_matrix_values(self, change):
        """Update the appropriate matrix value when a Combo select change"""
        
        # get the code of the class in the src classification
        code = change['owner']._metadata['class']
        
        # bind it to classes in the dst classification
        self.model.matrix[code] = change['new']
        
        return self
        
class ReclassifyView(v.Card):
    """
    Stand-alone Card object allowing the user to reclassify a input file. the input can be of any type (vector or raster) and from any source (local or GEE). 
    The user need to provide a destination classification file (table) in the following format : 3 headless columns: 'code', 'desc', 'color'. Once all the old class have been attributed to their new class the file can be exported in the source format to local memory or GEE. the output is also savec in memory for further use in the app. It can be used as a tile in a sepal_ui app. The id_ of the tile is set to "reclassify_tile"
    
    Args:
        model (ReclassifyModel): the reclassify model to manipulate the classification dataset. default to a new one
        class_path (str,optional): Folder path containing already existing classes. Default to ~/
        out_path (str,optional): the folder to save the created classifications. default to ~/downloads
        gee (bool): either or not to set :code:`gee` to True. default to False
        dst_class (str|pathlib.Path, optional): the file to be used as destination classification. for app that require specific code system the file can be set prior and the user won't have the oportunity to change it
        default_class (dict|optional): the default classification system to use, need to point to existing sytem: {name: absolute_path}
        
    Attributes:
        model (ReclassifyModel): the reclassify model to manipulate the classification dataset
        gee (bool): either being linked to gee or not (use local file or GEE asset for the rest of the app)
        alert (sw.Alert): the alert to display informations about computation
        title (v.Cardtitle): the title of the card
        w_asset (sw.AssetSelect): the widget to select an asset input 
        w_raster (sw.FileInput): the widget to select a file input
        w_image (Any): wraper of the input. linked to w_asset if gee=True, else to w_raster
        w_code (int|str): widget to select the band/property used as init classification in the input file
        get_table_btn (sw.Btn): the btn to load the data in the reclassification table
        w_class_file (sw.FileInput): widget to select the new classification system file (3 headless columns: 'code', 'desc', 'color')
        reclassify_table (ReclassifyTable): the reclassification table populated via the previous widgets
        reclassify_btn (sw.Btn): the btn to launch the reclassifying process
    """

    def __init__(self, model=None, class_path=Path.home(), out_path=Path.home()/'downloads', gee=False, dst_class=None, default_class={}, **kwargs):
        
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
                
        # set the title of the card
        self.title = v.CardTitle(children=[v.Html(tag='h2', children=[ms.rec.rec.title])])
        
        # create the input widgets
        w_input_title = v.Html(tag='h2', children=[ms.rec.rec.input.title], class_='mt-5')
        
        self.w_asset = sw.AssetSelect(label=ms.rec.rec.input.asset)
        self.w_raster = sw.FileInput(['.tif', '.vrt', '.tiff', '.geojson', '.shp'], label=ms.rec.rec.input.file)
        self.w_image = self.w_asset if self.gee else self.w_raster
        
        self.w_code = v.Select(label=ms.rec.rec.input.band.label, hint=ms.rec.rec.input.band.hint, v_model=None, items=[], persistent_hint=True)
        
        self.w_name = v.Select(label='select the class name from a property', hint='blablabla', v_model=None, items=None, persistent_hint=True)
        
        self.w_init_class_file = sw.FileInput(['.csv'], label='ini class', folder=self.class_path)
        w_optional_title = v.Html(tag='h3', children=['Optional'], class_='mb-5')
        
        w_optional = v.Alert(dense=True, text=True, class_='mt-5', color='light', children=[w_optional_title, self.w_name, self.w_init_class_file])
        
        # create the destination class widgetss
        w_class_title = v.Html(tag='h2', children=[ms.rec.rec.input.classif.title], class_='mt-5')
        self.w_class_file = sw.FileInput(['.csv'], label=ms.rec.rec.input.classif.label, folder=self.class_path)
        if dst_class:
            self.w_class_file.select_file(dst_class).hide()
            
        btn_list = [sw.Btn(f'use {name}', _metadata={'path': path}, small=True, class_='mr-2') for name, path in default_class.items()]
        w_default = v.Flex(children=btn_list)
        
        # set the table and its toolbar
        w_table_title = v.Html(tag='h2', children=[ms.rec.rec.table], class_='mt-5')
        
        self.save_dialog = SaveMatrixDialog(folder=out_path)
        self.get_table = sw.Btn(ms.rec.rec.input.btn, 'mdi-table', color='success', small=True)
        self.import_table = sw.Btn('import', 'mdi-download', color='secondary', small=True, class_='ml-2 mr-2')
        self.save_table = sw.Btn('save', 'mdi-content-save', small=True)
        self.reclassify_btn = sw.Btn(ms.rec.rec.btn, 'mdi-checkerboard', small=True)
        
        toolbar = v.Toolbar(
            class_='d-flex mb-6',
            flat=True, 
            children=[
                self.save_dialog,
                v.ToolbarTitle(children=['Actions']),
                v.Divider(class_='mx-4', inset=True, vertical=True),
                v.Flex(class_='ml-auto', children=[self.get_table, self.import_table, self.save_table]),
                v.Divider(class_='mx-4', inset=True, vertical=True),
                self.reclassify_btn
            ]
        )
        
        self.reclassify_table = ReclassifyTable(self.model)
        
        # bind to the model
        # bind to the 2 raster and asset as they cannot be displayed at the same time
        self.model \
            .bind(self.w_raster, 'src_local') \
            .bind(self.w_asset, 'src_gee') \
            .bind(self.w_code, 'band') \
            .bind(self.w_class_file, 'dst_class_file')
        
        # create the layout
        self.children = [
            self.title,
            w_input_title, self.w_image, self.w_code, w_optional,
            w_class_title, self.w_class_file, w_default,
            self.alert,
            w_table_title, toolbar, self.reclassify_table,
        ]
             
        # Decorate functions
        self.reclassify = loading_button(self.alert, self.reclassify_btn, debug=True)(self.reclassify)
        self.get_reclassify_table = loading_button(self.alert, self.get_table, debug=True)(self.get_reclassify_table)

        # JS Events
        self.save_table.on_event('click', lambda *args: self.save_dialog.show(self.model.matrix))
        self.w_image.observe(self._update_band, 'v_model')
        self.get_table.on_event('click', self.get_reclassify_table)
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
        self.w_code.v_model = None
        self.w_code.items = self.model.get_bands()
        
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
        if not self.w_code.v_model: raise AttributeError('missing band')
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
        