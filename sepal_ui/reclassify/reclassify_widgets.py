from functools import partial
from traitlets import Int, link, Dict
from ipywidgets import Output
import ipyvuetify as v 
from sepal_ui import sepalwidgets as sw
from sepal_ui.message import ms

class Dialog(v.Dialog):
    
    def __init__(self, widget, *args, **kwargs):
        
        
        self.v_model=False
        self.max_width=436
        self.overlay_color='black'
        self.overlay_opcity=0.7
        
        self.w_save =  sw.Btn('Ok', class_='ml-2 my-2')
        
        self.children=[
            v.Card(children=[
                v.CardTitle(children=['Reclassify to new values']),
                widget, 
                self.w_save, 
            ]),
        ]

        super().__init__(*args, **kwargs)
        
        self.w_save.on_event('click', self.save)
    
    def save(self, *args):
        self.v_model=False
    
    def show(self):
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
        
    
class ReclassifyTable(v.SimpleTable, sw.SepalWidget):
    
    matrix = Dict({}).tag(sync=True)
    
    def __init__(self, *args, **kwargs):
        """Widget to reclassify raster/feature_class into local classes"""
        
        self.dense = True

        # Create table
        super().__init__(*args, **kwargs)
        

    def _get_matrix(self, code_fields, classes_file=''):
        """ Init table reading local classes file and code/categories fields
        
        Args:
            code_fields (list) : List of codes/categories of raster/feature collection
            classes_file (str) : Classes file containing code/category and description
        """
        
        
        self.matrix = {}
        
        # Set empty items if there is not a file selected
        self.items = []
        
        if classes_file: self.items = self.read_classes_from_file(classes_file)
        
        headers = ['From: user code', 'To: Custom Code']
        
        # Instantiate an empty dictionary with code as 
        # keys and empty values
        for code in code_fields:
            self.matrix[code] = ''
            
        header = [
            v.Html(
                tag = 'tr', 
                children = (
                    [v.Html(tag = 'th', children = [h]) for h in headers]
                )
            )
        ]
        
        rows = [
            v.Html(tag='tr', children=[
                v.Html(tag = 'td', children=[str(code)]), 
                self.get_classes(code),
                
            ]) for code in code_fields
        ]
        
        self.children = [v.Html(tag = 'tbody', children = header + rows)]
        
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
        

    def get_classes(self, code):
        """ Get class selector on the fly and store code to matrix
        
        Args:
            code (str) : id to link local (raster, fc) with new classes (from file)
        """
                
        select = v.Combobox(
            _metadata={'name':code}, 
            items=self.items, 
            v_model=None, 
            dense=True,
            hide_details=True,
#             type='number'
        )
        
        select.observe(partial(self.store, code), 'v_model')
        
        #Trigger the event and save it into the matrix
        select.v_model = int(code)
        
        return select