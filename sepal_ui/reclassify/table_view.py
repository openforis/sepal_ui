from pathlib import Path
from colorsys import rgb_to_hls, rgb_to_hsv
from traitlets import Int, Dict, link

from ipywidgets import Output
import ipyvuetify as v
from matplotlib.colors import to_rgb
import pandas as pd

from sepal_ui import sepalwidgets as sw 
from sepal_ui.scripts import utils as su
from sepal_ui.message import ms


class ClassTable(v.DataTable, sw.SepalWidget):
    
    """ 
    Custom data table to modify, display and save classification. From this interface, a user can modify a classification starting from a scratch or by loading a classification file. the display datatable allow all the CRUD fonctionality (create, read, update, delete).
    
    Attributes:
        SCHEMA (const list): the schema of the classification: ['id', 'code', 'description', 'color']
        out_path (pathlib.Path): the output folder to save the created classifications
        save_dialog (v.Dialog): the Dialog to save the classification (select name and format)
        edit_dialog (v.Dialog): the dialog to edit/create a noew line in the data-table. The user will provide: the code, the description and the color (with a color selector)
        edit_icon (v.Icon): the btn to open the edit_dialog (a line need to be selected in the table)
        delete_icon (v.icon): the btn to delete a selected line in the table
        add_icon (v.Icon): the btn to add a new line in the table
        save_icon (v.Icon): the btn to open the save_dialog and save the current classification table
        
    Args:
        out_path (str|optional): output path where table will be saved, default to ~/downloads/
    """
    
    SCHEMA = ['id', 'code', 'description', 'color']
        
    def __init__(self, out_path=Path.home()/'downloads', **kwargs):
        
        # save the output path
        self.out_path =Path(out_path)
        
        # create the dialogs
        self.save_dialog = SaveDialog(table=self, out_path=self.out_path, transition=False)
        self.edit_dialog = EditDialog(table=self)

        # create the 4 CRUD btn 
        # and set them in the top slot of the table
        self.edit_btn = sw.Btn('edit', icon='mdi-pencil', class_='ml-2 mr-2', color='secondary', small=True) #v.Icon(children=['mdi-pencil'])
        #edit_icon = sw.Tooltip(self.edit_icon, 'Edit selected row', bottom=True)
        
        self.delete_btn = sw.Btn('delete', icon='mdi-delete', color='error', small=True) #v.Icon(children=['mdi-delete'], color='error')
        #delete_icon = sw.Tooltip(self.delete_icon, 'Permanently delete the selected row',  bottom=True)
        
        self.add_btn = sw.Btn('add', icon='mdi-plus', color='success', small=True) #v.Icon(children=['mdi-plus'], color='success')
        #add_icon = sw.Tooltip(self.add_icon, 'Create a new element',  bottom=True)
        
        self.save_btn = sw.Btn('save', icon='mdi-content-save', small=True) #v.Icon(children=['mdi-content-save'])
        #save_icon = sw.Tooltip(self.save_icon, 'Write current table on SEPAL space',  bottom=True)
        
        slot = v.Toolbar(
            class_='d-flex mb-6',
            flat=True, 
            children=[
                self.edit_dialog,
                self.save_dialog,
                v.ToolbarTitle(children=['Actions']),
                v.Divider(class_='mx-4', inset=True, vertical=True),
                v.Flex(class_='ml-auto', children=[self.add_btn, self.edit_btn, self.delete_btn]),
                v.Divider(class_='mx-4', inset=True, vertical=True),
                self.save_btn
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
        self.edit_btn.on_event('click', self._edit_event)
        self.delete_btn.on_event('click', self._remove_event)
        self.add_btn.on_event('click', self._add_event)
        self.save_btn.on_event('click', self._save_event)
        
    def populate_table(self, items_file=None):
        """ 
        Populate table. It will fill the table with the item contained in the items_file parameter. If no file is provided the table is reset.

        Args:
            items (Path object|optional): file containing classes and description
            
        Return:
            self
        """
        
        # If there is not any file passed as an argument, populate and empy table
        if not items_file:
            self.items = []
            return self
        
        # if there is, retrieve the content of the file to populate the table
        
        items = []
        # read the file using pandas
        df = pd.read_csv(items_file, header=None)
        
        # small sanity check 
        if not len(df.columns) in [2,3]:
            raise Exception('The file is not a valid classification file')
        
        # add a color column if necessary 
        if len(df.columns) == 2:
            df[2] = ['#000000' for _ in range(len(df))]
        
        # set the lines
        self.items = [dict(zip(self.SCHEMA, [i] + row.tolist())) for i, row in df.iterrows()]
        
        return self
    
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
    Dialog to modify/create new elements from the ClassTable data_table
        
    Args: 
        table (ClassTable, v.DataTable): Table linked with dialog
        
    Attributes:
        TITLE (list): the list of potential header (translated at the start of the application)
        table (classTable): the classTable associated with the dialog 
        title (v.CardTitle): the title of the card ('modify' or 'new')
        save (sw.Btn): the btn to validate the new line and save it in the datatable
        modify (sw.Btn): the btn to validate the edited line and save it in the datatable
        cancel (sw.Btn): the btn to close the dialog without saving anything
        widgets (list): the list of widget to control the new element state (id, code, description, color) in this order.
    """
    
    TITLE = ["New element", "Modify element"]
    
    def __init__(self, table, **kwargs):

        # custom attributes 
        self.table = table
        
        # set the title
        self.title = v.CardTitle(children=[self.TITLE[0]])
        
        # Action buttons
        self.save = sw.Btn('Save')
        save_tool = sw.Tooltip(self.save, 'Create new element',  bottom=True)
        
        self.modify = sw.Btn('Modify').hide() # by default modify is hidden
        modify_tool = sw.Tooltip(self.modify, 'Update row', bottom=True)
        
        self.cancel = sw.Btn('Cancel', outlined=True, class_='ml-2')
        cancel_tool = sw.Tooltip(self.cancel, 'Ignore changes',  bottom=True)
        
        actions = v.CardActions(children=[save_tool, modify_tool, cancel_tool])
        
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
        """
        upadte the dialog with the provided information and activate it
        
        Args:
            data (list): the text value of the selected line (id, code, description, color). default to 4 None (new line)
            
        Return:
            self
        """
        
        # change the title accodring to the presence of data
        self.title.children = [self.TITLE[not any(data)]]
        
        # change the btns visiblity
        if not any(data):
            self.save.show()
            self.modify.hide()
        else:
            self.save.hide()
            self.modify.show()
        
        # change the content
        for i, item in enumerate(zip(self.widgets, data)):
            
            widget, val = item
            
            # textfield can be filled directly
            if i != 3: 
                widget.v_model = val 
                
            # the color picker need to be set in every color format to work
            else: 
                
                # default to red if no value is provided
                val = val if val else '#FF0000'
                
                rgb = [int(i*255) for i in to_rgb(val)]
                hls = rgb_to_hls(*to_rgb(val)) 
                hsv = rgb_to_hsv(*to_rgb(val))
                
                # rebuild all the colors from the hex code
                # the full v_model need to provided to see the color in the colorpicker
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
        """Modify elements in the data_table and close the dialog"""
        
        # modify a local copy of the items
        # modifying does not trigger the display so a dummy element is also added
        # just to be removed afterward
        current_items = self.table.items.copy()
        for i, item in enumerate(current_items):
            if item['id'] == self.widgets[0].v_model:
                for j, w in enumerate(self.widgets):
                    val = w.v_model if j != 3 else w.v_model['hex']
                    current_items[i][self.table.SCHEMA[j]] = val
        current_items.append([str(e) for e in [0, 0, 'niet', '#000000']])
        
        # update the table values
        self.table.items = current_items
        
        # remove the dummy element to trigger the display
        self.table.items = self.table.items.copy()[:-1]
        
        # hide the dialog
        self.v_model=False
        
        # deselect the value for next time 
        # if not deselected the previous item will remain in the v_model 
        self.table.v_model = []
        
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
        
        # hide the dialog
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
        table (ClassTable): Table linked with dialog
        out_path (str): Folder path to store table content
        
    Attributes: 
        reload (Int): a traitlet to inform the rest of the app that saving is complete
        table (ClassTable): Table linked with dialog
        out_path (str): Folder path to store table content
        w_file_name (v.TextField): the filename to use in out_path
        save (sw.Btn): save btn to launch the saving of the table data in the out_path using the filename provided in the widget
        cancel (sw.Btn): btn to close the dialog and do nothing
        alert (sw.Alert): an alert to display evolution of the saving process (errors)
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
        
        # assemlble the layout
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
        """
        display the dialog and write down the text in the alert
        
        Return:
            self
        """
        
        self.v_model = True
        
        # the message is display after the show so that it's not cut by the display
        self.alert.add_msg(f'The table will be stored in {self.out_path}')
        
        return self
        
    def _normalize_name(self, widget, event, data):
        """Replace the name with it's normalized version"""
        
        # normalized the name
        widget.v_model = su.normalize_str(widget.v_model)

        return
    
    def _save(self, widget, event, data):
        """Write current table on a text file"""
        
        # set the file name
        out_file = self.out_path/su.normalize_str(self.w_file_name.v_model)
        
        # write each line values but not the id 
        lines = [list(item.values())[1:] for item in self.table.items]
        txt = [','.join(str(e) for e in l)+'\n' for l in lines]
        out_file.with_suffix('.csv').write_text(''.join(txt))
        
        # Every time a file is saved, we update the current widget state
        # so it can be observed by other objects.
        self.reload += 1
        
        self.v_model = False
        
        return
        
    def _cancel(self, widget, event, data):
        """hide the widget and do nothing"""
        
        self.v_model = False
        
        return

class TableView(v.Card, sw.SepalWidget):
    """
    Stand-alone Card object allowing the user to build custom class table. The user can start from an existing table or start from scratch. It gives the oportunity to change: the value, the class name and the color. It can be used as a tile in a sepal_ui app. The id_ of the tile is set to "classification_tile"
        
    Args:
        class_path (str|optional): Folder path containing already existing classes. Default to ~/
        out_path (str|optional): the folder to save the created classifications. default to ~/downloads
        
    Attributes:
        title (v.CardTitle): the title of the card
        class_path (str|optional): Folder path containing already existing classes
        out_path (str|optional): the folder to save the created classifications
        w_class_file (sw.FileInput): the file input of the existing classification system
        w_class_table (ClassTable): the classtable (CRUD) to manage the editing of the classification
        btn (sw.Btn): the btn to start loading file data into the table
        alert (sw.Alert): the alert to display loading information (error and success)
        
    """
    
    def __init__(self, class_path=Path.home(), out_path=Path.home()/'downloads', **kwargs):
        
        # create metadata to make it compatible with the framwork app system
        self._metadata = {'mount_id':'reclassify_tile'}
        
        # set some default params 
        self.class_ = 'pa-5'
        
        # init the card
        super().__init__(**kwargs)
        
        # set the folders
        self.class_path = Path(class_path)
        self.out_path = Path(out_path)
        
        # set a title to the card
        self.title = v.CardTitle(children=[v.Html(tag='h2', children=["Classification editor"])])
        
        # add the widgets
        w_class_title = v.Html(tag='h2', children=['Select preexisting table'], class_='mt-2')
        self.w_class_file = sw.FileInput(
            extentions = ['.csv'],
            label='class file',
            folder = self.class_path
        )
        
        self.btn = sw.Btn(ms.reclassify.get_custom_table_btn, icon='mdi-table', color='success', outlined=True)
        
        w_table_title = v.Html(tag='h2', children=['Classification table'], class_='mt-5')
        self.w_class_table = ClassTable(out_path=self.out_path, class_='mt-5')
        
        # create an alert to display error and outputs
        self.alert = sw.Alert()
        
        # assemble a layout
        self.children=[
            self.title,
            w_class_title, self.w_class_file, self.btn,
            self.alert,
            w_table_title, self.w_class_table
        ]
        
        # Events
        self.btn.on_event('click', self.get_class_table)
    
    @su.loading_button(debug=True)
    def get_class_table(self, widget, event, data):
        """
        Display class table widget in view
        
        Return:
            self
        """

        # load the existing file into the table
        self.w_class_table.populate_table(self.w_class_file.v_model)
        
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