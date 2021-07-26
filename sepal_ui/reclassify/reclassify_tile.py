from pathlib import Path
import ipyvuetify as v
from sepal_ui import sepalwidgets as sw
from sepal_ui.message import ms
from sepal_ui import reclassify as rec
from traitlets import link

class ReclassifyTile(sw.Tile):
    
    def __init__(self, results_dir, gee=True, save=True, **kwargs):
        
        """All in one tile to reclassify GEE assets or local raster 
        
        Args:
            results_dir (str|pathlike object) : Directory to store the 
                                outputs (rasters, and csv_files)
            
            gee (bool) : Use GEE variant, to reclassify assets 
                        or local raster. default True
                        
            save (bool): Write GEE assets or Raster's. If False, 
                        the reclassified objects could  be accessed in 
                        tile.model.raster_reclass or tile.model.reclass_ee

        """

        self._metadata = {'mount_id':'reclassify_tile'}
        
        # output directory
        # ensure it's initialized
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # create the model
        self.model = rec.ReclassifyModel(self.results_dir)
        
        # set the tabs elements
        self.reclassify_view = rec.ReclassifyView(self.results_dir, gee, save)
        self.reclassify_view.elevation = False
        self.table_view = rec.TableView()
        self.table_view.elevation = False
        
        # create the tab 
        titles = {
            'reclassify': self.reclassify_view,
            'table': self.table_view 
        }
        
        self.tabs = v.Tabs(
            v_model=0,
            children=[
                v.Tab(children=[title], key=key) 
                for key, title in enumerate(titles.keys())
            ]
        )
        
        self.content = v.TabsItems(
            v_model=0,
            children=[
                v.TabItem(children=[content], key=key) 
                for key, content in enumerate(titles.values())
            ]
        )
        
        super().__init__(
            id_ = 'reclassify_tile',
            title = 'Reclassification',
            inputs = [self.tabs, self.content],
            **kwargs
        )
        
        # js interaction
        link((self.tabs, 'v_model'),(self.content, 'v_model'))
