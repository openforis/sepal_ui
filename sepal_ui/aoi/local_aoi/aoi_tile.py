from sepal_ui import sepalwidgets as sw 
from sepal_ui import mapping as sm
import ipyvuetify as v

from sepal_ui.aoi.local_aoi.aoi_view import *

class AoiTile(sw.Tile):
    
    def __init__(self, methods='ALL', **kwargs):
        
        # create the map 
        self.map=sm.SepalMap(dc=True)
        
        # create the view
        # the view include the model 
        self.aoi_view = AoiView(methods=methods, map=self.map)
        
        # organise them in a layout
        layout = v.Layout(
            row      = True,
            xs12     = True,
            children = [
                v.Flex(xs12 = True, md6 = True, children = [self.aoi_view]),
                v.Flex(xs12 = True, md6 = True, class_ = "pa-5", children = [self.map])
            ]
        )

        
        # create the tile
        super().__init__(
            "aoi_tile",
            "Select AOI",
            inputs = [layout]
        )