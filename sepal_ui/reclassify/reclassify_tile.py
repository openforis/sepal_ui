from pathlib import Path
from traitlets import link

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw
from sepal_ui.message import ms
from sepal_ui import reclassify as rec

class ReclassifyTile(sw.Tile):
    """
    All in one tile to reclassify GEE assets or local raster and create custom classifications
        
    Args:
        results_dir (str|pathlike object) : Directory to store the outputs (rasters, and csv_files). default to ~/downloads
        gee (bool) : Use GEE variant, to reclassify assets or local input. default True
    """
    
    def __init__(self, results_dir=Path.home()/'downloads', gee=True, **kwargs):
        
        # output directory
        self.results_dir = Path(results_dir)
        
        # create the model
        self.model = rec.ReclassifyModel(dst_dir=self.results_dir, gee=gee)
        
        # set the tabs elements
        self.reclassify_view = rec.ReclassifyView(self.model, out_path=self.results_dir, gee=gee).nest_tile()        
        self.table_view = rec.TableView(out_path=self.results_dir).nest_tile()
        
        # create the tab 
        tiles = [self.reclassify_view, self.table_view]
        
        self.tabs = v.Tabs(
            class_='mt-5',
            grow=True,
            #background_color='grey darken-4',
            v_model=0,
            children=[
                v.Tab(children=[t.title.children[0].children[0]], key=i) 
                for i, t in enumerate(tiles)
            ]
        )
        
        self.content = v.TabsItems(
            v_model=0,
            children=[
                v.TabItem(children=[t], key=i) 
                for i, t in enumerate(tiles)
            ]
        )
        
        super().__init__(
            id_ = 'reclassify_tile',
            title = ms.rec.tile.title,
            inputs = [self.tabs, self.content],
            **kwargs
        )
        
        # js interaction
        link((self.tabs, 'v_model'),(self.content, 'v_model'))
