from pathlib import Path

from sepal_ui import sepalwidgets as sw 
import ipyvuetify as v
from sepal_ui.scripts import utils as su
from sepal_ui.message import ms

from .customize_table import ClassTable



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