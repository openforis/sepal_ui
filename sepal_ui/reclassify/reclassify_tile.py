from pathlib import Path
import ipyvuetify as v
from sepal_ui.sepalwidgets import SepalWidget
from sepal_ui.reclassify import (
    ReclassifyView, CustomizeView, 
    ReclassifyTable, Tabs, 
)

class ReclassifyTile(v.Card, SepalWidget):
    
    def __init__(self, gee=True, *args, **kwargs):

        self.class_ = 'pa-4'
        self._metadata = {'mount_id':'reclassify'}

        super().__init__(*args, **kwargs)
        
        # Class parameters
                
        self.root_dir=None
        self.class_path=None
        self.workspace()
        
        self.w_reclassify_table = ReclassifyTable()
        self.reclassify_view = ReclassifyView(
            gee=gee,
            class_path=self.class_path,
            w_reclassify_table = self.w_reclassify_table
        )
        self.customize_view = CustomizeView(class_path=self.class_path)
        
        tabs_titles = ['Reclassify', 'Customize classification']
        tab_content = [
            self.reclassify_view,
            self.customize_view
        ]

        self.children=[
            Tabs(tabs_titles, tab_content)
        ]

    def workspace(self):
        """ Creates the workspace necessary to store the data

        return:
            returns env paths
        """

        base_dir = Path('~').expanduser()

        root_dir = base_dir/'module_results/gwb'
        class_path = root_dir/'custom_classification'

        root_dir.mkdir(parents=True, exist_ok=True)
        class_path.mkdir(parents=True, exist_ok=True)

        self.root_dir = root_dir
        self.class_path  = class_path