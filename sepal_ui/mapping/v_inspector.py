import ipyvuetify as v
from ipyleaflet import WidgetControl

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su


class VInspector(WidgetControl):

    m = None
    "(ipyleaflet.Map) the map on which he vinspector is displayed to interact with it's layers"

    menu = None

    card = None

    text = None

    def __init__(self, m, **kwargs):

        # load the map
        self.m = m

        # set some default parameters
        kwargs["position"] = kwargs.pop("position", "bottomright")

        # create a clickable btn
        icon = sw.Icon(small=True, children=["mdi-cloud-download"])
        btn = v.Btn(
            v_on="menu.on",
            color="text-color",
            outlined=True,
            style_="padding: 0px; min-width: 0px; width: 30px; height: 30px;",
            children=[icon],
        )
        slot = {"name": "activator", "variable": "menu", "children": btn}
        title = sw.CardTitle(children=[sw.Html(tag="h4", children=["Inspector"])])
        self.text = sw.CardText(children=["select a point"])
        self.card = sw.Card(
            children=[title, self.text], min_width="400px", min_height="200px"
        )

        # assempble everything in a menu
        self.menu = sw.Menu(
            v_model=False,
            value=False,
            close_on_click=False,
            close_on_content_click=False,
            children=[self.card],
            v_slots=[slot],
            offset_x=True,
            top="bottom" in kwargs["position"],
            bottom="top" in kwargs["position"],
            left="right" in kwargs["position"],
            right="left" in kwargs["position"],
        )

        super().__init__(widget=self.menu, **kwargs)

        # add js behaviour
        self.menu.observe(self.toggle_cursor, "v_model")
        self.m.on_interaction(self.read_data)

    def toggle_cursor(self, change):
        """
        Toggle the cursor displa on the map to notify to the user that the inspector mode is activated
        """

        cursors = [{"cursor": "grab"}, {"cursor": "crosshair"}]
        self.m.default_style = cursors[self.menu.v_model]

        return

    @su.switch("loading", on_widgets=["card"])
    def read_data(self, **kwargs):
        """
        Read the data when the map is clicked with the vinspector activated
        """
        # check if the v_inspector is active
        is_click = kwargs.get("type") == "click"
        is_active = self.menu.v_model is True
        if not (is_click and is_active):
            return

        # set the curosr to loading mode
        self.m.default_style = {"cursor": "wait"}

        # init the text children
        children = []

        # write the coordinates
        latlon = kwargs.get("coordinates")
        children.append(sw.Html(tag="h4", children=["Coordinates"]))
        children.append(sw.Html(tag="p", children=[str(latlon)]))

        # write the layers data
        children.append(sw.Html(tag="h4", children=["Layers"]))
        layers = [lyr for lyr in self.m.layers if lyr.base is False]
        for lyr in layers:
            children.append(sw.Html(tag="h5", children=[lyr.name]))
            children.append(
                sw.Html(tag="p", children=["data reading method not yet ready"])
            )

        # set them in the card
        self.text.children = children

        # set back the cursor to crosshair
        self.m.default_style = {"cursor": "crosshair"}

        return
