from pathlib import Path
from colorsys import rgb_to_hls, rgb_to_hsv

from sepal_ui import sepalwidgets as sw 
import ipyvuetify as v
from sepal_ui.scripts import utils as su
from sepal_ui.message import ms

from functools import partial
from pathlib import Path
from traitlets import Int, Dict, link
from ipywidgets import Output
import ipyvuetify as v
import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import utils as su
from matplotlib.colors import to_rgb
import pandas as pd


class ClassTable(v.DataTable, sw.SepalWidget):
    
    """ 
    Custom data table to display classification .csv files with features to create, edit or remove rows.
        
    Args:
        out_path (str|optional): output path where table will be saved, default to ~/downloads/
        
    Attributes:
        out_path
        dialog
        edit_icon
        delete_icon
        add_icon
        save_icon
        save_dialog
        SCHEMA
    """
    
    SCHEMA = ['id', 'code', 'description', 'color']
        
    def __init__(self, out_path=Path.home()/'downloads', **kwargs):
        
        # set the class general attributes
        self.out_path =Path(out_path)
        
        # dialogs
        self.save_dialog = SaveDialog(table=self, out_path=self.out_path, transition=False)
        self.edit_dialog = EditDialog(table = self)

        # create the 4 CRUD btn 
        # and set them in the top slot of the table
        self.edit_icon = v.Icon(children=['mdi-pencil'])
        edit_icon = sw.Tooltip(self.edit_icon, 'Edit selected row', bottom=True)
        
        self.delete_icon = v.Icon(children=['mdi-delete'])
        delete_icon = sw.Tooltip(self.delete_icon, 'Permanently delete the selected row',  bottom=True)
        
        self.add_icon = v.Icon(children=['mdi-plus'])
        add_icon = sw.Tooltip(self.add_icon, 'Create a new element',  bottom=True)
        
        self.save_icon = v.Icon(children=['mdi-content-save'])
        save_icon = sw.Tooltip(self.save_icon, 'Write current table on SEPAL space',  bottom=True)
        
        slot = v.Toolbar(
            class_='d-flex mb-6',
            flat=True, 
            children=[
                self.edit_dialog,
                self.save_dialog,
                v.ToolbarTitle(children=['Actions']),
                v.Divider(class_='mx-4', inset=True, vertical=True),
                v.Flex(class_='ml-auto', children=[edit_icon, delete_icon, add_icon]),
                v.Divider(class_='mx-4', inset=True, vertical=True),
                save_icon
            ]
        )
        
        self.v_slots = [{
            'name': 'top',
            'variable': 'top',
            'children': [slot]
        }]
        
        
        # set up default parameters of the datatable
        self.v_model = []
        self.item_key = 'id'
        self.show_select = True
        self.single_select = True
        self.hide_default_footer = True
        self.headers = [{'text': k.capitalize(), 'value': k} for k in self.SCHEMA]
        
        # create the object
        super().__init__(**kwargs)
        
        # js events
        self.edit_icon.on_event('click', self._edit_event)
        self.delete_icon.on_event('click', self._remove_event)
        self.add_icon.on_event('click', self._add_event)
        self.save_icon.on_event('click', self._save_event)
        
    def populate_table(self, items_file=None):
        """ 
        Populate table. It will fill the table with the item contained in the items_file. 
        If no file is provided the table is reset.

        Args:
            items (Path object|optional): file containing classes and description

        """
        
        # If there is not any file passed as an argument, populate and empy table
        # if there is retreive the content of the file to populate the table
        self.items = [] if not items_file else self.get_items_from_txt(items_file)
    
    def get_items_from_txt(self, items_path):
        """Read txt file with classification and transform it into a dict formatted to populate the table"""
        
        items = []
        keys = self.SCHEMA
        
        # read the file using pandas
        df = pd.read_csv(items_path, header=None)
        
        # small sanity check 
        if len(df.columns)<2 or len(df.columns)>3:
            raise Exception('The file is not a valid classification file')
        
        # add a color column if necessary 
        if len(df.columns) == 2:
            df[2] = ['#000000' for _ in range(len(df))]
        
        for i, row in df.iterrows():
            items.append(dict(zip(keys, [i] + row.tolist())))
                
        return items
    
    def _save_event(self, widget, event, data):
        """open the save dialog to save the current table in a specific formatted table"""
        
        if not self.items:
            return 
        
        self.save_dialog.v_model=True
            
        return
            
    def _edit_event(self, widget, event, data):
        """Open the edit dialog and fill it with current line information"""
        
        if not self.v_model:
            return 
        
        self.edit_dialog.update([v for v in self.v_model[0].values()])
            
        return 
                    
    def _add_event(self, widget, event, data):
        """Open the edit dialog to create a new line to the table"""

        self.edit_dialog.update()
        
        return
        
    def _remove_event(self, widget, event, data):
        """Remove current selection (self.v_model) element from table"""
        
        if not self.v_model:
            return 
        
        current_items = self.items.copy()
        current_items.remove(self.v_model[0])
        
        self.items = current_items
        
        return
    
class EditDialog(v.Dialog):
    
    """
    Dialog to modify/create new elements from the ClassTable data table
        
    Args: 
        table (ClassTable, v.DataTable): Table linked with dialog
        default (dict): Dictionary with default values of a edited row
    
    Attributes:
        table
        default
        title
    
    """
    
    model = Dict().tag(sync=True)
    
    TITLE = ["New element", "Modify element"]
    
    def __init__(self, table, **kwargs):

        # custom attributes 
        self.table = table
        self.default = None
        
        # set the title
        self.title = v.CardTitle(children=[self.TITLE[0]])
        
        # Action buttons
        self.save = sw.Btn('Save')
        self.save_tool = sw.Tooltip(self.save, 'Create new element',  bottom=True)
        
        self.modify = sw.Btn('Modify').hide() # by default modify is hidden
        self.modify_tool = sw.Tooltip(self.modify, 'Update row', bottom=True)
        
        self.cancel = sw.Btn('Cancel', outlined=True, class_='ml-2')
        cancel_tool = sw.Tooltip(self.cancel, 'Ignore changes',  bottom=True)
        
        actions = v.CardActions(children=[self.save_tool, self.modify_tool, cancel_tool])
        
        # create the widgets 
        self.widgets = [
            v.TextField(label=self.table.SCHEMA[0], type='number', v_model=None),
            v.TextField(label=self.table.SCHEMA[1], type='number', v_model=None),
            v.TextField(label=self.table.SCHEMA[2], type='string', v_model=None),
            v.ColorPicker(label=self.table.SCHEMA[3], mode='hexa', v_model=None)
        ]
        
        self.widgets[0].disabled = True # it's the id
        
        # some default params 
        self.v_model=False
        self.max_width=500
        self.overlay_opcity=0.7
        
        # create the object
        super().__init__(**kwargs)
        
        # add the widget to the dialog 
        self.children=[v.Card(
            class_='pa-4',
            children=[self.title] + self.widgets + [actions]
        )] 
        
        # Create events
        self.save.on_event('click', self._save)
        self.modify.on_event('click', self._modify)
        self.cancel.on_event('click', self._cancel)
        
    def update(self, data=[None,None,None,None]):
        """upadte the dialog with the provided information and activate it"""
        
        # change the title
        self.title.children = [self.TITLE[not any(data)]]
        
        # change the btns 
        if not any(data):
            self.save.show()
            self.modify.hide()
        else:
            self.save.hide()
            self.modify.show()
        
        # change the content
        for i, item in enumerate(zip(self.widgets, data)):
            
            widget, val = item
            if i != 3: 
                widget.v_model = val 
            else: 
                
                #default to red if no value is provided
                val = val if val else '#FF0000'
                
                rgb = [int(i*255) for i in to_rgb(val)]
                hls = rgb_to_hls(*to_rgb(val)) 
                hsv = rgb_to_hsv(*to_rgb(val))
                
                #rebuild all the colors from the hex code 
                widget.v_model = {
                    'alpha': 1,
                    'hex': val,
                    'hexa': f'{val}FF',
                    'hsla': {'h': hls[0], 's': hls[2], 'l': hls[1], 'a': 1},
                    'hsva': {'h': hsv[0], 's': hsv[1], 'v': hsv[2], 'a': 1},
                    'hue': hsv[0],
                    'rgba': {'r': rgb[0], 'g': rgb[1], 'b': rgb[2], 'a': 1}
                }
        
        # if nothing is set I need to specify a new id value 
        # this value should not interfere with the currently existing one. I'll thus just take the biggest +1
        if not any(data):
            self.widgets[0].v_model = 1 if not self.table.items else max([i['id'] for i in self.table.items])+1
        
        # activate it
        self.v_model = True
        
        return self
        
    def _modify(self, widget, event, data):
        """Modify elements in the table and close the dialog"""
        
        # modify a local copy of the items
        current_items = self.table.items.copy()
        for i, item in enumerate(current_items):
            if item['id'] == self.widgets[0].v_model:
                for j, w in enumerate(self.widgets):
                    val = w.v_model if j != 3 else w.v_model['hex']
                    current_items[i][self.table.SCHEMA[j]] = val
        
        # update the table values
        self.table.items = current_items
        
        # hide the dialog
        self.v_model=False
        
        return
    
    def _save(self, widget, event, data):
        """Add elements to the table and close the dialog"""
        
        # modify a local copy of the items
        current_items = self.table.items.copy()
        
        item_to_add = {}
        for i, w in enumerate(self.widgets):
            item_to_add[self.table.SCHEMA[i]] = w.v_model if i != 3 else w.v_model['hex']
            
        current_items.insert(0,item_to_add)
        
        # update the table values
        self.table.items = current_items
        
        #hide the dialog
        self.v_model=False
        
        return
        
    def _cancel(self, widget, event, data):
        """Close dialog and do nothing"""
        
        self.v_model=False
        
        return
        
        
class SaveDialog(v.Dialog):
    
    """
    Dialog to save as .csv file the content of a ClassTable data table
        
    Args: 
        table (ClassTable, v.DataTable): Table linked with dialog
        out_path (str): Folder path to store table content
        
    Attributes: 
        reload
    """
    
    reload = Int().tag(sync=True)
        
    def __init__(self, table, out_path, **kwargs):
        
        # gather the table and saving params 
        self.table = table
        self.out_path = out_path
        
        # set some default parameters
        self.max_width=500
        self.v_model = False
        
        # create the widget
        super().__init__(**kwargs)
        
        # build widgets
        self.w_file_name = v.TextField(label='Insert output file name', v_model='new_table')
        
        self.save = sw.Btn('Save')
        save = sw.Tooltip(self.save, 'Save table', bottom=True, class_='pr-2')
        
        self.cancel = sw.Btn('Cancel', outlined=True, class_='ml-2')
        cancel = sw.Tooltip(self.cancel, 'Cancel', bottom=True)
        
        self.alert = sw.Alert()
        
        # asselble the layout
        self.children=[v.Card(
            class_='pa-4',
            children=[
                v.CardTitle(children=['Save table']),
                self.w_file_name,
                self.alert,
                save,
                cancel
            ]
        )]
        
        # Create events
        self.save.on_event('click', self._save)
        self.cancel.on_event('click', self._cancel)
        self.w_file_name.on_event('blur', self._normalize_name)
        
    def show():
        """display the dialog and write down the text in the alert"""
        
        self.v_model = True
        
        # the message is display after the show so that it's not cut by the display
        self.alert.add_msg(f'The table will be stored in {self.out_path}')
        
        return self
        
    def _normalize_name(self, widget, event, data):
        """replace the name with it's normalized version"""
        
        # normalized the name
        widget.v_model = su.normalize_str(widget.v_model)

        return
    
    def _save(self, *args):
        """Write current table on a text file"""
        
        # set the file name
        out_file = self.out_path/su.normalize_str(self.w_file_name.v_model)
        
        # read each line values but not the id 
        lines = [list(item.values())[1:] for item in self.table.items]
        txt = [','.join(l)+'\n' for l in lines]
        out_file.with_suffix('.csv').write_text(''.join(txt))
        
        # Every time a file is saved, we update the current widget state
        # so it can be observed by other objects.
        self.reload+=1
        
        self.v_model=False
        
        return
        
    def _cancel(self, *args):
        """hide the widget and do nothing"""
        
        self.v_model=False
        
        return

class TableView(v.Card, sw.SepalWidget):
    
    """
    Stand-alone Card object allowing the user to build custom class table. The user can start from an existing table or start from scratch. It gives the oportunity to change: the value, the class name and the color.
        
    Args:
        model (ReclassifyModel): The reclassify model to edit
        class_path (str|optional): Folder path containing classification tables
        
    Attributes:
        class_path
        w_class_file
        w_class_table
        
    """
    
    def __init__(self, class_path=None, **kwargs):
        
        # set some default params 
        self.class_ = 'pa-2'
        
        # init the card
        super().__init__(**kwargs)
        
        # set the save folder
        self.class_path = Path(class_path) if class_path else Path.home()
        
        # set a title to the card
        title = v.CardTitle(children=["Class table manager"])
        
        # add the widgets
        self.w_class_file = sw.FileInput(
            extentions = ['.csv'],
            label=ms.reclassify.class_file_label,
            folder = self.class_path
        )
        
        self.btn = sw.Btn(ms.reclassify.get_custom_table_btn, class_='ml-2')
        
        ep_optional_file = v.ExpansionPanels(children=[v.ExpansionPanel(class_= 'ma-5', children = [
            v.ExpansionPanelHeader(children=['Select preexisting table']),
            v.ExpansionPanelContent(children=[self.w_class_file, self.btn])
        ])])
        
        self.w_class_table = ClassTable(out_path=self.class_path)
        
        # create an alert to display error and outputs
        self.alert = sw.Alert()
        
        # assemble a layout
        self.children=[
            title,
            ep_optional_file,
            self.alert,
            self.w_class_table
        ]
        
        # Events
        self.btn.on_event('click', self.get_class_table)
    
    @su.loading_button(debug=True)
    def get_class_table(self, *args):
        """Display class table widget in view"""

        # load the existing file into the table
        self.w_class_table.populate_table(self.w_class_file.v_model)
        
        return self