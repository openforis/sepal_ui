from functools import partial
from pathlib import Path
from traitlets import Int, Dict, link
from ipywidgets import Output
import ipyvuetify as v
import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import utils as su


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
    
    SCHEMA = {'id':'number', 'code':'number', 'description':'string'}
        
    def __init__(self, out_path=Path.home()/'downloads', **kwargs):
        
        # set the class general attributes
        self.out_path =Path(out_path)
        
        # open a Output widget to display the edit and validation dialog
        # edit dialog 
        self.dialog = Output()
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
                self.dialog,
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
        self.headers = [{'text': k.capitalize(), 'value': k} for k in self.SCHEMA.keys()]
        
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
        keys = self.SCHEMA.keys()
        with open(items_path) as f:
            for i, line in enumerate(f.readlines()):
                item = [it.replace('\n','') if isinstance(it, str) else it for it in [i]+line.split(',')]
                items+=[(dict(zip(keys, item)))]
                
        return items
    
    def _save_event(self, widget, event, data):
        """open the save dialog to save the current table in a specific formatted table"""
        
        if not self.items:
            return 
        
        with self.dialog:
            self.dialog.clear_output()
            self.save_dialog.v_model=True
            display(self.save_dialog)
            
        return
            
    def _edit_event(self, widget, event, data):
        """Open the edit dialog and fill it with current line information"""
        
        if not self.v_model:
            return 
        
        with self.dialog:
            self.dialog.clear_output()
            self.edit_dialog.update([v for v in self.v_model[0]])
            display(self.edit_dialog)
            
        return 
                    
    def _add_event(self, widget, event, data):
        """Open the edit dialog to create a new line to the table"""
        
        with self.dialog:
            self.dialog.clear_output()
            self.edit_dialog.update()
            display(self.edit_dialog)
        
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
        self.widgets = [v.TextField(label=title.capitalize(), type=type_, v_model=None) for title, type_ in self.table.SCHEMA.items()]
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
        
    def update(self, data=[None,None,None]):
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
        for widget, val in zip(self.widgets, data):
            widget.v_model = val
        
        # if nothing is set I need to specify a new id value 
        # this value should not interfere with the currently existing one. I'll thus just take the biggest +1
        if not any(data):
            self.widgets[0].v_model = 1 if not self.table.items else max([i['id'] for i in self.table.items])+1
        
        # activate it
        self.v_model = True
        
        return self
        
    def _modify(self, widget, event, data):
        """Modify elements to the table and close the dialog"""
        
        # modify a local copy of the items
        current_items = self.table.items.copy()
        for i, item in enumerate(current_items):
            if item['id'] == self.widgets[0].v_model:
                current_items[i] = [{w.label.lower(): w.v_model} for w in self.widgets]
        
        # update the table values
        self.table.items = current_items
        
        # hide the dialog
        self.v_model=False
        
        return
    
    def _save(self, widget, event, data):
        """Add elements to the table and close the dialog"""
        
        # modify a local copy of the items
        current_items = self.table.items.copy()
        item_to_add = [{w.label.lower(): w.v_model} for w in self.widgets]
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
        
        with out_file.with_suffix('.csv').open('w') as f:
            
            # read each line values but the not the id 
            lines = [list(item.values())[1:] for item in self.table.items]
            
            # write the lines to a 
            for line in lines:
                f.write(",".join(line)+'\n')
        
        # Every time a file is saved, we update the current widget state
        # so it can be observed by other objects.
        self.reload+=1
        
        self.v_model=False
        
        return
        
    def _cancel(self, *args):
        """hide the widget and do nothing"""
        
        self.v_model=False
        
        return
    
