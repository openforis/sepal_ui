from pathlib import Path
import ipyvuetify as v
from sepal_ui.sepalwidgets import SepalWidget
from sepal_ui.reclassify import (
    ReclassifyView, CustomizeView, 
    ReclassifyTable, Tabs, ReclassifyModel
)
from sepal_ui.message import ms

class ReclassifyTile(v.Card, SepalWidget):
    
    def __init__(self, 
                 gee=True, 
                 save=True,
                 *args, **kwargs):
        
        """All in one tile to reclassify GEE assets or local raster 
        
        Args:
            
            gee (bool) : Use GEE variant, to reclassify assets or local raster
                        default True
                        
            save (bool): Write GEE assets or Raster's. If False, the reclassified objects could 
                        be accessed in tile.model.raster_reclass or tile.model.reclass_ee_image
                        
            map (bool): Whether a map will display the reclassify assets or not.

        """

        self.class_ = 'pa-4'
        self._metadata = {'mount_id':'reclassify'}

        super().__init__(*args, **kwargs)
        
        # Class parameters
                
        self.root_dir=None
        self.class_path=None
        self.workspace()
        self.model = ReclassifyModel()
        
        
        self.w_reclassify_table = ReclassifyTable()
        self.view = ReclassifyView(
            self.model,
            w_reclassify_table = self.w_reclassify_table,
            class_path=self.class_path,
            gee=gee,
            save=save,
            map_=map_
        )
        self.customize_view = CustomizeView(
            self.model,
            class_path=self.class_path
        )
        
        tabs_titles = ['Reclassify', 'Customize classification']
        tab_content = [
            self.view,
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

        root_dir = base_dir/'downloads'
        class_path = root_dir/'custom_classification'

        root_dir.mkdir(parents=True, exist_ok=True)
        class_path.mkdir(parents=True, exist_ok=True)

        self.root_dir = root_dir
        self.class_path  = class_path