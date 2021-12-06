import ipyvuetify as v

from sepal_ui import sepalwidgets as sw
from sepal_ui import mapping as sm
from sepal_ui.message import ms

from sepal_ui.aoi.aoi_view import AoiView

__all__ = ["AoiTile"]


class AoiTile(sw.Tile):
    """
    sw.Tile tailored for the selection of an aoi. it is meant to be used with the aoi. it can be bound to EarthEngine (GAUl 2015 administrative definition) or stay with the GADM Python implementation

    Args:
        methods (list, optional): the methods to select the aoi (more information in AoiView), default to 'ALL'. Available: {‘ADMIN0’, ‘ADMIN1’, ‘ADMIN2’, ‘SHAPE’, ‘DRAW’, ‘POINTS’, ‘ASSET’, ‘ALL’}
        ee (bool, optional): wether or not to use the python EartEngine API. default to True
        vector (str|pathlib.Path, optional): the path to the default vector object
        admin (int, optional): the administrative code of the default selection. Need to be GADM if ee==False and GAUL 2015 if ee==True.
        asset (str, optional): the default asset. Can only work if :code:`ee==True`.
    """

    map = None
    "sepal_ui.mapping.SepalMap: a SepalMap object to display the selected aoi"

    view = None
    "widget: an AoiView object to handle the aoi method selection"

    def __init__(self, methods="ALL", gee=True, **kwargs):

        # create the map
        self.map = sm.SepalMap(dc=True, gee=gee)

        # create the view
        # the view include the model
        self.view = AoiView(methods=methods, map_=self.map, gee=gee, **kwargs)
        self.view.elevation = 0

        # organise them in a layout
        layout = v.Layout(
            row=True,
            xs12=True,
            children=[
                v.Flex(xs12=True, md6=True, class_="pa-5", children=[self.view]),
                v.Flex(xs12=True, md6=True, class_="pa-1", children=[self.map]),
            ],
        )

        # create the tile
        super().__init__("aoi_tile", ms.aoi_sel.title, inputs=[layout], **kwargs)
