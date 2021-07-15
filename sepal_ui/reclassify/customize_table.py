from functools import partial
from pathlib import Path
from traitlets import Int, Dict, link
from ipywidgets import Output
import ipyvuetify as v
import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import utils as su


class ClassTable(v.DataTable, sw.SepalWidget):
    
        
    def __init__(self, 
                 schema,
                 out_path=Path('~').expanduser()/'downloads', 
                 *args, **kwargs):
        
        """ Custom data table to display classification .csv files with features to create,
        edit or remove rows.
        
        Args: 
            schema (dict): schema (dict {'title':'type'}): Dictionary 
                with column names (key) and type of data (value), representing the scheme
                of the table.

            out_path (str) (optional): output path where table will be saved, default to ~/downloads/
        """
        
        self.out_path = out_path
        self.schema = schema
        self.dialog = Output()

        self.edit_icon = v.Icon(children=['mdi-pencil'])
        edit_icon = sw.Tooltip(self.edit_icon, 'Edit selected row', bottom=True)
        
        self.delete_icon = v.Icon(children=['mdi-delete'])
        delete_icon = sw.Tooltip(self.delete_icon, 'Permanently delete the selected row',  bottom=True)
        
        self.add_icon = v.Icon(children=['mdi-plus'])
        add_icon = sw.Tooltip(self.add_icon, 'Create a new element',  bottom=True)
        
        self.save_icon = v.Icon(children=['mdi-content-save'])
        save_icon = sw.Tooltip(self.save_icon, 'Write current table on SEPAL space',  bottom=True)
        self.save_dialog = SaveDialog(table=self, out_path=self.out_path, transition=False)
        
        slot = v.Toolbar(
            class_='d-flex mb-6',
            flat=True, 
            children=[
                self.dialog,
                v.ToolbarTitle(children=['Customization tools']),
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
        
        self.v_model = []
        self.item_key = 'id'
        self.show_select = True
        self.single_select = True
        self.hide_default_footer = True
        
        super().__init__(*args, **kwargs)
        
        
        self.edit_icon.on_event('click', self._edit_event)
        self.delete_icon.on_event('click', self._remove_event)
        self.add_icon.on_event('click', self._add_event)
        self.save_icon.on_event('click', self._save_event)
        
    def populate_table(self, items_file):
        """ Populate table, it will fill the table with the .csv items_file

        Args:
            items (.txt): file containing classes and description

        """
        self.headers =  [
            {'text': k.capitalize(), 'value': k} for k in self.schema.keys() if k!='id'
        ]
        
        # If there is not any file passed as an argument, populate and empy table
        # with the given scheme or s
        self.items = [] if items_file == '' else self.get_items_from_txt(items_file)
    
    def get_items_from_txt(self, items_path):
        """Read txt file with classification"""
        
        items = []
        keys = self.schema.keys()
        with open(items_path) as f:
            for i, line in enumerate(f.readlines()):
                item = [it.replace('\n','') if isinstance(it, str) else it for it in [i]+line.split(',')]
                items+=[(dict(zip(keys, item)))]
                
        return items
    
    def _save_event(self, widget, event, data):
        
        if not self.items:
            return 
        
        with self.dialog:
            self.dialog.clear_output()
            self.save_dialog.v_model=True
            display(self.save_dialog)
            
        return
            
    def _edit_event(self, widget, event, data):
        
        if not self.v_model:
            return 

        dial = EditDialog(
            schema = self.schema, 
            default = self.v_model[0],
            table = self,
            transition = False
        )
        with self.dialog:
            display(dial)
            
        return 
                    
    def _add_event(self, widget, event, data):
        
        dial = EditDialog(
            schema = self.schema, 
            table = self
        )
        with self.dialog:
            display(dial)
        
        return
        
    def _remove_event(self, widget, event, data):
        """Remove current selected (self.v_model) element from table"""
        
        if not self.v_model:
            return 
        
        current_items = self.items.copy()
        current_items.remove(self.v_model[0])
        
        self.items = current_items
        
        return
    
class EditDialog(v.Dialog):
    
    model = Dict().tag(sync=True)
    
    def __init__(self, table, schema, *args, default = None, **kwargs):
        """
        
        Dialog to modify/create new elements from the ClassTable data table
        
        Args: 
            table (ClassTable, v.DataTable): Table linked with dialog
            schema (dict {'title':'type'}): Schema for table showing headers and type of data
            default (dict): Dictionary with default values of a edited row
        """
        
        self.schema = schema
        self.table = table
        self.default = default
        self.title = "New element" if not self.default else "Modify element"
        self.v_model=True
        self.max_width=500
        self.overlay_opcity=0.7
        
        # Action buttons
        self.save = sw.Btn('Save')
        save_tool = sw.Tooltip(self.save, 'Create new element',  bottom=True)
        
        self.cancel = sw.Btn('Cancel', outlined=True, class_='ml-2')
        cancel_tool = sw.Tooltip(self.cancel, 'Ignore changes',  bottom=True)
        
        self.modify = sw.Btn('Modify')
        modify_tool = sw.Tooltip(self.modify, 'Update row', bottom=True)
        
        save = [save_tool, cancel_tool]
        modify = [modify_tool, cancel_tool]
        
        actions = v.CardActions(children=save if not default else modify)
        
        super().__init__(*args, **kwargs)
        
        self.children=[
            v.Card(
                class_='pa-4',
                children=[
                    v.CardTitle(children=[self.title])] + \
                    self._get_widgets() + \
                    [actions]
            )
        ] 
        
        # Create events
        self.save.on_event('click', self._save)
        self.modify.on_event('click', self._modify)
        self.cancel.on_event('click', self._cancel)
        
    def _modify(self, widget, event, data):
        """Modify elements to the table"""
        
        current_items = self.table.items.copy()
        
        for i, item in enumerate(current_items):
            if item['id'] == self.model['id']:
                current_items[i] = self.model
        
        self.table.items = current_items
        self.v_model=False
    
    def _save(self, widget, event, data):
        """Add elements to the table"""
        
        current_items = self.table.items.copy()
        item_to_add = self.model
        new_items = [item_to_add] + current_items
        
        self.table.items = new_items
        self.v_model=False
                
    def _get_index(self):
        """Get an unique index for a new element"""
        
        index = 1 if not self.table.items else max([i['id'] for i in self.table.items])+1
        return index
        
    def _cancel(self, widget, event, data):
        """Close dialog"""
        
        self.v_model=False
    
    def _populate_dict(self, change, title):
        """Populate model with new values"""
        self.model[title] = change['new'] if change['new'] else change['old']
    
    def _get_widgets(self):
        
        """Create widgets on fly"""
        
        widgets = []
        for title, type_ in self.schema.items():

            widget = v.TextField(label=title.capitalize(), type=type_, v_model=None)
            widget.observe(partial(self._populate_dict, title=title), 'v_model')
                        
            if title == 'id': widget.disabled=True
                
            if self.default: 
                widget.v_model = self.default[title] if title in self.default else None
            else:
                if title=='id': widget.v_model = self._get_index()
                
            widgets.append(widget)
            
        return widgets
        
        
class SaveDialog(v.Dialog):
    
    reload = Int().tag(sync=True)
        
    def __init__(self, table, out_path, *args, **kwargs):
        """
        
        Dialog to save as .csv file the content of a ClassTable data table
        
        Args: 
            table (ClassTable, v.DataTable): Table linked with dialog
            out_path (str): Folder path to store table content
        """
        self.max_width=500
        self.v_model = False
        self.out_path = out_path
        
        super().__init__(*args, **kwargs)
        
        self.table = table
        
        self.w_file_name = v.TextField(
            label='Insert output file name', 
            type='string', 
            v_model='new_table'
        )
        
        # Action buttons
        self.save = sw.Btn('Save')
        save = sw.Tooltip(self.save, 'Save table', bottom=True, class_='pr-2')
        
        self.cancel = sw.Btn('Cancel', outlined=True, class_='ml-2')
        cancel = sw.Tooltip(self.cancel, 'Cancel', bottom=True)
        
        info = sw.Alert().add_msg(
            'The table will be stored in {}'.format(str(out_path))).show()
                
        self.children=[
            v.Card(
                class_='pa-4',
                children=[
                    v.CardTitle(children=['Save table']),
                    self.w_file_name,
                    info,
                    save,
                    cancel
                ]
            )
        ]
        
        # Create events
        self.save.on_event('click', self._save)
        self.cancel.on_event('click', self._cancel)
        self.w_file_name.on_event('blur', self._normalize_name)
        
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
            for line in self._get_lines():
                f.write(",".join(line)+'\n')
        
        # Every time a file is saved, we update the current widget state
        # so it can be observed by other objects.
        self.reload+=1
        
        self.v_model=False
        
        return
        
    def _cancel(self, *args):
        self.v_model=False
        
        return
            
    def _get_lines(self):
        """Get list of lines from table"""
        # Skip the first element: 'id' on table
        return [list(item.values())[1:] for item in self.table.items]
    
