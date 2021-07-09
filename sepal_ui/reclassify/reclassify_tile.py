from pathlib import Path
import ipyvuetify as v
from sepal_ui.sepalwidgets import SepalWidget
from sepal_ui.reclassify import (
    ReclassifyView, CustomizeView, 
    ReclassifyTable, Tabs, ReclassifyModel
)
from sepal_ui.message import ms

class ReclassifyTile(Tabs, SepalWidget):
    
    def __init__(self, 
                 results_dir,
                 gee=True, 
                 save=True,
                 *args, **kwargs):
        
        """All in one tile to reclassify GEE assets or local raster 
        
        Args:
            results_dir (str) : Directory to store the 
                                outputs (rasters, and csv_files)
            
            gee (bool) : Use GEE variant, to reclassify assets 
                        or local raster. default True
                        
            save (bool): Write GEE assets or Raster's. If False, 
                        the reclassified objects could  be accessed in 
                        tile.model.raster_reclass or tile.model.reclass_ee

        """

        self._metadata = {'mount_id':'reclassify'}
        
        # Class parameters
                
        self.results_dir = results_dir if results_dir else Path('~').expanduser()/'downloads'
        self.class_dir = results_dir/'custom_classifications'
        
        Path(self.class_dir).mkdir(parents=True, exist_ok=True)

        self.model = ReclassifyModel(results_dir)
        
        
        self.w_reclassify_table = ReclassifyTable()
        self.view = ReclassifyView(
            self.model,
            w_reclassify_table = self.w_reclassify_table,
            class_path=self.class_dir,
            gee=gee,
            save=save
        )
        self.customize_view = CustomizeView(
            self.model,
            class_path=self.class_dir
        )
        
        tabs_titles = ['Reclassify', 'Customize classification']
        tab_content = [
            self.view,
            self.customize_view
        ]
        
        super().__init__(titles=tabs_titles,
                         content=tab_content,
                         *args, **kwargs)
