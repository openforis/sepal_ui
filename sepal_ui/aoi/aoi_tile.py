import ipyvuetify as v

from sepal_ui import sepalwidgets as sw 
from sepal_ui import mapping as sm
from sepal_ui.message import ms

from sepal_ui.aoi.aoi_view import *

class AoiTile(sw.Tile):
    
    def __init__(self, methods='ALL', ee= True, **kwargs):
        
        # create the map 
        self.map=sm.SepalMap(dc=True, ee=ee)
        
        # create the view
        # the view include the model 
        self.aoi_view = AoiView(methods=methods, map_=self.map, ee=ee)
        self.aoi_view.elevation = 0
        
        # organise them in a layout
        layout = v.Layout(
            row      = True,
            xs12     = True,
            children = [
                v.Flex(xs12 = True, md6 = True, class_="pa-5", children = [self.aoi_view]),
                v.Flex(xs12 = True, md6 = True, class_ = "pa-1", children = [self.map])
            ]
        )

        # create the tile
        super().__init__(
            "aoi_tile",
            "Select AOI",
            inputs = [layout]
        )