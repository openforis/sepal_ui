import ee
from shapely import geometry as sg
from ipyleaflet import WidgetControl

from sepal_ui.mapping.map_btn import MapBtn
from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su


class AoiControl(WidgetControl):
    """
    Widget control providing zoom options for the end user. The developer can add as many gemetries to the widget and the user will simply have to click on them to move to the appropriate AOI.

    Args:
        m (ipyleaflet.Map): the map on which he AoiControl is displayed to interact with itszoom and center
    """

    m = None
    "(ipyleaflet.Map): the map on which he AoiControl is displayed to interact with itszoom and center"

    aoi_bounds = None
    "(list): the list of ListItem used in the menu. each one as the name provided by the user and the value of the bounds"

    def __init__(self, m, **kwargs):

        # load the map
        self.m = m

        # init the aoi data list
        self.aoi_bounds = {}

        # set some default parameters
        kwargs["position"] = kwargs.pop("position", "topright")

        # create a hoverable btn
        btn = MapBtn(logo="fas fa-at", v_on="menu.on")
        slot = {"name": "activator", "variable": "menu", "children": btn}
        self.aoi_list = sw.ListItemGroup(children=[], v_model="")
        w_list = sw.List(
            dense=True,
            flat=True,
            v_model=True,
            max_height="300px",
            min_width="200px",
            max_width="200px",
            tile=True,
            style_="overflow: auto;",
            children=[self.aoi_list],
        )

        # assemble everything in a menu
        self.menu = sw.Menu(
            v_model=False,
            value=False,
            close_on_click=False,
            children=[w_list],
            open_on_click=False,
            open_on_hover=True,
            v_slots=[slot],
            offset_x=True,
            top="bottom" in kwargs["position"],
            bottom="top" in kwargs["position"],
            left="right" in kwargs["position"],
            right="left" in kwargs["position"],
        )

        super().__init__(widget=self.menu, **kwargs)

        # add js behaviours
        btn.on_event("click", self.click_btn)
        self.aoi_list.observe(self.zoom, "v_model")

    def click_btn(self, widget, event, data):
        """
        Zoom to the total area of all AOIs in :code:`self.aoi_bounds`. Use the whole world if empty
        """

        # set the bounds to the world if the list is empty
        if len(self.aoi_bounds) == 0:
            bounds = (-180, -90, 180, 90)
        else:
            minx = min([i[0] for i in self.aoi_bounds.values()])
            miny = min([i[1] for i in self.aoi_bounds.values()])
            maxx = max([i[2] for i in self.aoi_bounds.values()])
            maxy = max([i[3] for i in self.aoi_bounds.values()])
            bounds = (minx, miny, maxx, maxy)

        self.m.zoom_bounds(bounds)

        return

    @su.need_ee
    def add_aoi(self, name, item):
        """
        Add an AOI to the list and refresh the list displayed. the AOI will be composed of a name and the bounds of the provided item.

        Args:
            name (str): the name of the AOI
            item (Geometry|ee.ComputedObject): the item to use to compute the bounds. It need to be a shapely geometry or an ee object.
        """

        if isinstance(item, ee.ComputedObject):
            # extract bounds from ee_object
            ee_geometry = item if isinstance(item, ee.Geometry) else item.geometry()
            bl, br, tr, tl, _ = ee_geometry.bounds().coordinates().get(0).getInfo()
            bounds = (*bl, *tr)

        elif isinstance(item, sg.base.BaseGeometry):
            bounds = item.bounds

        else:
            raise ValueError("Cannot extract bounds from the input")

        self.aoi_bounds[name] = bounds

        # update the list
        self.update_list()

        return

    def remove_aoi(self, name):
        """
        Remove an item from the :code:`self.aoi_bounds` dict and from the ListItem. It will raise a KeyError if the name cannot be found

        Args:
            name (str): the name of the aoi to remove
        """

        # remove the value from the list
        self.aoi_bounds.pop(name)

        # update the list
        self.update_list()

        return

    def zoom(self, change):
        """
        Zoom on the specified bounds

        Args:
            change["new"]: a tuple of the bounds of the geometry (minx, miny, maxx, maxy)
        """

        self.m.zoom_bounds(change["new"])

        return

    def update_list(self):
        """
        Update the ListItem children of the object based on the content of :code:`self.aoi_bounds`
        """

        children = []

        for name, bounds in self.aoi_bounds.items():

            text = sw.ListItemContent(children=[sw.ListItemTitle(children=[name])])
            item = sw.ListItem(dense=True, value=bounds, children=[text])
            children.append(item)

        self.aoi_list.children = children

        return
