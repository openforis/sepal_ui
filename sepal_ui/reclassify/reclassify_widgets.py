from pathlib import Path
from functools import partial
from traitlets import Int, link, Dict
from ipywidgets import Output
import ipyvuetify as v 
from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su
from sepal_ui.message import ms

class EditTableDialog(v.Dialog):
    """Edit dialog tile to load, reclassify and save classes"""
    
    def __init__(self, model, folder=Path.home(), alert=sw.Alert(), **kwargs):
        
        self.v_model=False
        self.max_width=650
        self.overlay_color='black'
        self.overlay_opcity=0.7
        
        # Input widgets
        self.reclassify_table = ReclassifyTable()
        
        super().__init__(**kwargs)
        
        # bind the alert to the provided one 
        # if non a default one will be created
        self.alert = alert
        
        self.load_btn = sw.Btn('Load values', class_='ml-1')
        self.input_file = sw.FileInput(['.csv'], folder)
        
        w_panel_load = v.ExpansionPanels(children=[
            v.ExpansionPanel(children=[
                v.ExpansionPanelHeader(children=['Use a custom csv file']),
                v.ExpansionPanelContent(children=[
                    v.Flex(class_='d-flex align-center',
                        children=[
                            self.input_file,
                            self.load_btn
                        ]
                    )
                ])
            ])
        ])

        self.w_save =  sw.Btn('Ok', class_='ml-2 my-2')
        self.w_save_matrix = SaveReclass(model, folder)
        
        self.save_matrix_btn = sw.Btn('Save table', x_small=True)
        
        # create the layout
        self.children=[
            v.Card(children=[
                self.w_save_matrix, # This is a dialog
                v.CardTitle(children=['Reclassify to new values']),
                self.alert,
                w_panel_load,
                self.reclassify_table, 
                v.Flex(children=[self.save_matrix_btn]),
                self.w_save, 
            ]),
        ]
        
        # Decorate functions
        self.save_matrix = su.loading_button(self.alert, self.save_matrix_btn, debug=True)(self.save_matrix)
        self.load_csv_file = su.loading_button(self.alert, self.load_btn, debug=True)(self.load_csv_file)
        
        # js events
        self.w_save.on_event('click', self.save)
        self.save_matrix_btn.on_event('click', self.save_matrix)
        self.load_btn.on_event('click', self.load_csv_file)
        
    def load_csv_file(self, *args):
        """Read input .csv file, and fill combos with its data"""
        
        csv_file = self.input_file.v_model
        self.reclassify_table.fill_combos_from_file(csv_file)
        
    def save_matrix(self, *args):
        """Open save reclass dialog"""
        self.w_save_matrix.v_model = True
    
    def save(self, *args):
        """Close dialog"""
        self.v_model=False
    
    def show(self):
        """Display dialog"""
        self.v_model=True
        

            
class Tabs(v.Card):
    
    current = Int(0).tag(sync=True)
    
    def __init__(self, titles, content, **kwargs):
        
        self.background_color="primary"
        self.dark = True
        
        self.tabs = [v.Tabs(v_model=self.current, children=[
            v.Tab(children=[title], key=key) for key, title in enumerate(titles)
        ])]
        
        self.content = [v.TabsItems(
            v_model=self.current, 
            children=[
                v.TabItem(children=[content], key=key) for key, content in enumerate(content)
            ]
        )]
        
        self.children= self.tabs + self.content
        
        link((self.tabs[0], 'v_model'),(self.content[0], 'v_model'))
        
        super().__init__(**kwargs)
        

class ClassSelector(v.Combobox, sw.SepalWidget):
    """
    class selector combobox to select an existing class or create on the fly a new one. 
    When a item list is provided, it will be used as preloaded class name
    
    Args:
        code (int): id to link local (raster, fc) with new classes (from file)
        items (list): the list of items to preload in the object
        
    """
    def __init__(self, code, items, **kwargs):
        
        super().__init__(
            _metadata={'name': code},
            items=items,
            dense=True,
            hide_details=True,
            v_model = int(code)
        )
        
        
class ReclassifyTable(v.SimpleTable, sw.SepalWidget):
    
    matrix = Dict({}).tag(sync=True)
    
    def __init__(self, *args, **kwargs):
        """Widget to reclassify raster/feature_class into local classes"""
        
        # each combobox selector will be gathered in a list 
        self.combos = {}
        
        # default parameters 
        self.dense = True

        # Create table
        super().__init__(*args, **kwargs)

    def _get_matrix(self, code_fields, classes_file=''):
        """ Init table reading local classes file and code/categories fields
        
        Args:
            code_fields (list) : List of codes/categories of raster/feature collection
            classes_file (str) : Classes file containing code/category and description
        """
        
        # Set empty items if there is not a file selected
        self.items = self.read_classes_from_file(classes_file) if classes_file else []
        
        headers = ['From: user code', 'To: Custom Code']
        
        # Instantiate an empty dictionary with code as keys and default value 
        self.matrix = {code: int(code) for code in code_fields}
            
        # init the class selectors
        # and link it to the matrix
        self.combos = {code: ClassSelector(code, self.items) for code in code_fields}
        [self.combos[code].observe(partial(self.store, code), 'v_model') for code in code_fields]
            
        # init the table header and rows 
        header = [v.Html(tag='tr', children=[v.Html(tag = 'th', children = [h]) for h in headers])]
        rows = [
            v.Html(tag='tr', children=[
                v.Html(tag='td', children=[str(code)]), 
                v.Html(tag='td', children=[self.combos[code]])
            ]) for code in code_fields
        ]
        
        self.children = [v.Html(tag='tbody', children= header + rows)]
        
        return self
                       
    def read_classes_from_file(self, class_file):
        """ Read classes from .csv file
        
        Args:
            class_file (str): classes .csv file containing lines of (code_class, description)
        """
        items = []
        with open(class_file) as f:
            for cl in f.readlines():
                # c:code, d:description
                item = [
                    {'value': int(c), 'text': f'{c}: ' + d.replace('\n','')} for c, d 
                    in [cl.split(',')]
                ]
                items+=item
                
        return items
        
    def store(self, code, change):
        """Store user row code and new select value (file class)"""
        self.matrix[code] = change['new']
    
    def fill_combos_from_file(self, csv_file):
        """Fill combos v_model from a csv_file
        
        Args:
            csv_file (str): Path of previous saved matrix as csv file
        """
        
        with open(csv_file, 'r') as f:
            for cl in f.readlines():
                from_, to = cl.split(',')
                from_=int(from_)
                to=int(to.replace('\n',''))
                self.combos[int(from_)].v_model=to
    
    
class SaveReclass(v.Dialog):
    
    reload = Int().tag(sync=True)
        
    def __init__(self, model, out_path, *args, **kwargs):
        """
        
        Dialog to save as .csv file the content of a ReclassifyTable data table
        
        Args: 
            matrix (ReclassifyTable.matrix): Reclassify table matrix
            out_path (str): Folder path to store table content
        """
        self.max_width=500
        self.v_model = False
        self.out_path = out_path
        
        super().__init__(*args, **kwargs)
        
        self.model = model
        
        self.w_file_name = v.TextField(
            label='Insert output file name', 
            type='string', 
            v_model='new_table.csv'
        )
        
        # Action buttons
        self.save = sw.Btn('Save')
        save = sw.Tooltip(self.save, 'Save table', bottom=True, class_='pr-2')
        
        self.cancel = sw.Btn('Cancel')
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
    
    def _save(self, *args):
        """Write current table on a text file"""
        
        file_name = self.w_file_name.v_model
        file_name = file_name.strip()
        if not '.csv'in file_name:
            file_name = f'{file_name}.csv'
        
        out_file = self.out_path/file_name
        
        print(self.model.matrix.items())
        
        with open(out_file, 'w') as f:
            for line in self.model.matrix.items():
                line = [str(l) for l in line]
                f.write(",".join(line)+'\n')
        
        # Every time a file is saved, we update the current widget state
        # so it can be observed by other objects.
        self.reload+=1
        
        self.v_model=False
        
    def _cancel(self, *args):
        self.v_model=False