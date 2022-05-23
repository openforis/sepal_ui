import ipyvuetify as v
from ipyleaflet import WidgetControl, GeoJSON
import ee
import geopandas as gpd
from shapely import geometry as sg

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su
from sepal_ui import color as sc
from sepal_ui.mapping.layer import EELayer


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
            style_=f"padding: 0px; min-width: 0px; width: 30px; height: 30px; background: {sc.bg};",
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

            if isinstance(lyr, EELayer):
                data = self._from_eelayer(lyr.ee_object, latlon)
            elif isinstance(lyr, GeoJSON):
                data = self._from_geojson(lyr.data, latlon)
            else:
                data = {"info": "data reading method not yet ready"}

            for k, val in data.items():
                children.append(sw.Html(tag="span", children=[f"{k}: {val}"]))
                children.append(sw.Html(tag="br", children=[]))

        # set them in the card
        self.text.children = children

        # set back the cursor to crosshair
        self.m.default_style = {"cursor": "crosshair"}

        return

    @su.need_ee
    def _from_eelayer(self, ee_obj, coords):
        """
        extract the values of the ee_object for the considered point

        Args:
            ee_obj (ee.object): the ee object to reduce to a single point
            coords (tuple): the coordinates of the point (lat, lng).

        Return:
            (dict): tke value associated to the bad/feature names
        """

        # create a gee point
        lat, lng = coords
        ee_point = ee.Geometry.Point(lng, lat)

        if isinstance(ee_obj, ee.FeatureCollection):

            # filter all the value to the point
            features = ee_obj.filterBounds(ee_point)

            # if there is none, print non for every property
            if features.size().getInfo() == 0:
                cols = ee_obj.first().propertyNames().getInfo()
                pixel_values = {c: None for c in cols if c not in ["system:index"]}

            # else simply return all the values of the first element
            else:
                pixel_values = features.first().toDictionary().getInfo()

        elif isinstance(ee_obj, (ee.Image)):

            # reduce the layer region using mean
            pixel_values = ee_obj.reduceRegion(
                geometry=ee_point,
                scale=self.m.get_scale(),
                reducer=ee.Reducer.mean(),
            ).getInfo()

        else:
            raise ValueError(
                f'the layer object is a "{type(ee_obj)}" which is not accepted.'
            )

        return pixel_values

    def _from_geojson(self, data, coords):
        """
        extract the values of the data for the considered point

        Args:
            data (GeoJSON): the shape to reduce to a single point
            coords (tuple): the coordinates of the point (lat, lng).

        Return:
            (dict): tke value associated to the feature names
        """

        # extract the coordinates as a point
        lat, lng = coords
        point = sg.Point(lng, lat)

        # filter the data to 1 point
        gdf = gpd.GeoDataFrame.from_features(data)
        gdf_filtered = gdf[gdf.contains(point)]

        # only display the columns name if empty
        if len(gdf_filtered) == 0:
            cols = list(set(["geometry", "style"]) ^ set(gdf.columns.to_list()))
            pixel_values = {c: None for c in cols}

        # else print the values of the first element
        else:
            pixel_values = gdf_filtered.iloc[0].to_dict()
            pixel_values.pop("geometry")
            pixel_values.pop("style")

        return pixel_values
