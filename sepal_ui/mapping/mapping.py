# knwon bug of rasterio
import os

if "GDAL_DATA" in list(os.environ.keys()):
    del os.environ["GDAL_DATA"]
if "PROJ_LIB" in list(os.environ.keys()):
    del os.environ["PROJ_LIB"]

import collections
from pathlib import Path
from distutils.util import strtobool

import geemap
from haversine import haversine
import numpy as np
import rioxarray
import xarray_leaflet  # do not remove: plugin for rioxarray so it is never called but always used
import matplotlib.pyplot as plt
from matplotlib import colors as mpc
from matplotlib import colorbar
import ipywidgets as widgets
from ipyleaflet import (
    AttributionControl,
    DrawControl,
    LayersControl,
    LocalTileLayer,
    ScaleControl,
    WidgetControl,
    ZoomControl,
)
from traitlets import Bool, link, observe
import ipyvuetify as v
import ipyleaflet
import ee

from sepal_ui.scripts import utils as su
from sepal_ui.message import ms

__all__ = ["SepalMap"]

# call x_array leaflet at least one
# flake8 will complain as it's a pluggin (i.e. never called)
# We don't want to ignore testing F401
xarray_leaflet


class SepalMap(geemap.Map):
    """
    The SepalMap class inherits from geemap.Map. It can thus be initialized with all its parameter.
    The map will fall back to CartoDB.DarkMatter map that well fits with the rest of the sepal_ui layout.
    Numerous methods have been added in the class to help you deal with your workflow implementation.
    It can natively display raster from .tif files and files and ee objects using methods that have the same signature as the GEE JavaScripts console.

    Args:
        basemaps ['str']: the basemaps used as background in the map. If multiple selection, they will be displayed as layers.
        dc (bool, optional): wether or not the drawing control should be displayed. default to false
        vinspector (bool, optional): Add value inspector to map, useful to inspect pixel values. default to false
        ee (bool, optional): wether or not to use the ee binding. If False none of the earthengine display fonctionalities can be used. default to True
        kwargs (optional): any parameter from a geemap.Map. if set, 'ee_initialize' will be overwritten.
    """

    # ############################################################################
    # ###                              Map parameters                          ###
    # ############################################################################

    ee = True
    "bool: either the map will use geempa binding or not"

    vinspector = Bool(False).tag(sync=True)
    "bool: either or not the datainspector is available"

    loaded_rasters = {}
    "dict: the list of loaded rasters"

    dc = None
    "ipyleaflet.DrawingControl: the drawing control of the map"

    def __init__(self, basemaps=[], dc=False, vinspector=False, gee=True, **kwargs):

        self.world_copy_jump = True

        # set the default parameters
        kwargs["ee_initialize"] = False  # we do it ourselves
        kwargs["add_google_map"] = kwargs.pop("add_google_map", False)
        kwargs["center"] = kwargs.pop("center", [0, 0])
        kwargs["zoom"] = kwargs.pop("zoom", 2)

        # Init the map
        super().__init__(**kwargs)

        # init ee
        self.ee = gee
        if gee:
            su.init_ee()

        # add the basemaps
        self.clear_layers()
        if len(basemaps):
            [self.add_basemap(basemap) for basemap in set(basemaps)]
        else:
            self.add_basemap("CartoDB.DarkMatter")

        # add the base controls
        self.clear_controls()
        self.add_control(ZoomControl(position="topright"))
        self.add_control(LayersControl(position="topright"))
        self.add_control(AttributionControl(position="bottomleft"))
        self.add_control(ScaleControl(position="bottomleft", imperial=False))

        # change the prefix
        for control in self.controls:
            if type(control) == AttributionControl:
                control.prefix = "SEPAL"

        # specific drawing control
        self.set_drawing_controls(dc)

        # Add value inspector
        self.w_vinspector = widgets.Checkbox(
            value=False,
            description="Inspect values",
            indent=False,
            layout=widgets.Layout(width="18ex"),
        )

        if vinspector:
            self.add_control(
                WidgetControl(widget=self.w_vinspector, position="topright")
            )

            link((self.w_vinspector, "value"), (self, "vinspector"))

        # Create output space for raster interaction
        self.output_r = widgets.Output(layout={"border": "1px solid black"})
        self.output_control_r = WidgetControl(
            widget=self.output_r, position="bottomright"
        )
        self.add_control(self.output_control_r)

        # define interaction with rasters
        self.on_interaction(self._raster_interaction)

    @observe("vinspector")
    def _change_cursor(self, change):
        """Method to be called when vinspector trait changes"""

        if self.vinspector:
            self.default_style = {"cursor": "crosshair"}
        else:
            self.default_style = {"cursor": "grab"}

        return

    def _raster_interaction(self, **kwargs):
        """Define a behavior when ispector checked and map clicked"""

        if kwargs.get("type") == "click" and self.vinspector:
            latlon = kwargs.get("coordinates")
            self.default_style = {"cursor": "wait"}

            local_rasters = [
                lr.name for lr in self.layers if isinstance(lr, LocalTileLayer)
            ]

            if local_rasters:

                with self.output_r:
                    self.output_r.clear_output(wait=True)

                    for lr_name in local_rasters:

                        lr = self.loaded_rasters[lr_name]
                        lat, lon = latlon

                        # Verify if the selected latlon is the image bounds
                        if any(
                            [
                                lat < lr.bottom,
                                lat > lr.top,
                                lon < lr.left,
                                lon > lr.right,
                            ]
                        ):
                            print("Location out of raster bounds")
                        else:
                            # row in pixel coordinates
                            y = int(((lr.top - lat) / abs(lr.y_res)))

                            # column in pixel coordinates
                            x = int(((lon - lr.left) / abs(lr.x_res)))

                            # get height and width
                            h, w = lr.data.shape
                            value = lr.data[y][x]
                            print(f"{lr_name}")
                            print(f"Lat: {round(lat,4)}, Lon: {round(lon,4)}")
                            print(f"x:{x}, y:{y}")
                            print(f"Pixel value: {value}")
            else:
                with self.output_r:
                    self.output_r.clear_output()

            self.default_style = {"cursor": "crosshair"}

            return

    def set_drawing_controls(self, add=False):
        """
        Create a drawing control for the map.
        It will be possible to draw rectangles, circles and polygons.

        Args:
            add (bool): either to add the dc to the object attribute or not

        return:
            self
        """

        color = v.theme.themes.dark.info

        dc = DrawControl(
            edit=False,
            marker={},
            circlemarker={},
            polyline={},
            rectangle={"shapeOptions": {"color": color}},
            circle={"shapeOptions": {"color": color}},
            polygon={"shapeOptions": {"color": color}},
        )

        self.dc = dc if add else None

        return self

    def _remove_local_raster(self, local_layer):
        """
        Remove local layer from memory

        Args:
            local_layer (str | geemap.layer): The local layer to remove or its name

        Return:
            self
        """
        name = local_layer if type(local_layer) == str else local_layer.name

        if name in self.loaded_rasters.keys():
            self.loaded_rasters.pop(name)

        return self

    def remove_last_layer(self, local=False):
        """
        Remove last added layer from Map

        Args:
            local (boolean): Specify True to only remove local last layers, otherwise will remove every last layer.

        Return:
            self
        """
        if len(self.layers) > 1:

            last_layer = self.layers[-1]

            if local:
                local_rasters = [
                    lr for lr in self.layers if isinstance(lr, LocalTileLayer)
                ]
                if local_rasters:
                    last_layer = local_rasters[-1]
                    self.remove_layer(last_layer)

                    # If last layer is local_layer, remove it from memory
                    if isinstance(last_layer, LocalTileLayer):
                        self._remove_local_raster(last_layer)
            else:
                self.remove_layer(last_layer)

                # If last layer is local_layer, remove it from memory
                if isinstance(last_layer, LocalTileLayer):
                    self._remove_local_raster(last_layer)

        return self

    @su.need_ee
    def zoom_ee_object(self, ee_geometry, zoom_out=1):
        """
        Get the proper zoom to the given ee geometry.

        Args:
            ee_geometry (ee.Geometry): the geometry to zoom on
            zoom_out (int) (optional): Zoom out the bounding zoom

        Return:
            self
        """

        # center the image
        self.centerObject(ee_geometry)

        # extract bounds from ee_object
        ee_bounds = ee_geometry.bounds().coordinates()
        coords = ee_bounds.get(0).getInfo()

        # Get (x, y) of the 4 cardinal points
        bl, br, tr, tl, _ = coords

        # Get (x, y) of the 4 cardinal points
        min_lon, min_lat = bl
        max_lon, max_lat = tr

        # zoom on these bounds
        self.zoom_bounds([min_lon, min_lat, max_lon, max_lat], zoom_out)

        return self

    def zoom_bounds(self, bounds, zoom_out=1):
        """
        Adapt the zoom to the given bounds. and center the image.

        Args:
            bounds ([coordinates]): coordinates corners as minx, miny, maxx, maxy
            zoom_out (int) (optional): Zoom out the bounding zoom

        Return:
            self
        """

        minx, miny, maxx, maxy = bounds

        # Center map to the centroid of the layer(s)
        self.center = [(maxy - miny) / 2 + miny, (maxx - minx) / 2 + minx]

        tl = (minx, maxy)
        bl = (minx, miny)
        tr = (maxx, maxy)
        br = (maxx, miny)

        maxsize = max(haversine(tl, br), haversine(bl, tr))

        lg = 40075  # number of displayed km at zoom 1
        zoom = 1
        while lg > maxsize:
            zoom += 1
            lg /= 2

        if zoom_out > zoom:
            zoom_out = zoom - 1

        self.zoom = zoom - zoom_out

        return self

    def add_raster(
        self,
        image,
        bands=None,
        layer_name="Layer_" + su.random_string(),
        colormap=plt.cm.inferno,
        x_dim="x",
        y_dim="y",
        opacity=1.0,
        fit_bounds=True,
        get_base_url=lambda _: "https://sepal.io/api/sandbox/jupyter",
        colorbar_position="bottomright",
    ):
        """
        Adds a local raster dataset to the map.

        Args:
            image (str | pathlib.Path): The image file path.
            bands (int or list, optional): The image bands to use. It can be either a number (e.g., 1) or a list (e.g., [3, 2, 1]). Defaults to None.
            layer_name (str, optional): The layer name to use for the raster. Defaults to None.
            colormap (str, optional): The name of the colormap to use for the raster, such as 'gray' and 'terrain'. More can be found at https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html. Defaults to None.
            x_dim (str, optional): The x dimension. Defaults to 'x'.
            y_dim (str, optional): The y dimension. Defaults to 'y'.
            opacity (float, optional): the opacity of the layer, default 1.0.
            fit_bounds (bool, optional): Wether or not we should fit the map to the image bounds. Default to True.
            get_base_url (callable, optional): A function taking the window URL and returning the base URL to use. It's design to work in the SEPAL environment, you only need to change it if you want to work outside of our platform. See xarray-leaflet lib for more details.
            colorbar_position (str, optional): The position of the colorbar (default to "bottomright"). set to False to remove it.
        """

        if type(image) == str:
            image = Path(image)

        if not image.is_file():
            raise Exception(ms.mapping.no_image)

        # check inputs
        if layer_name in self.loaded_rasters.keys():
            layer_name = layer_name + su.random_string()

        if isinstance(colormap, str):
            colormap = plt.cm.get_cmap(name=colormap)

        da = rioxarray.open_rasterio(image, masked=True)

        # The dataset can be too big to hold in memory, so we will chunk it into smaller pieces.
        # That will also improve performances as the generation of a tile can be done in parallel using Dask.
        da = da.chunk((1000, 1000))

        # Create a named tuple with raster bounds and resolution
        local_raster = collections.namedtuple(
            "LocalRaster",
            ("name", "left", "bottom", "right", "top", "x_res", "y_res", "data"),
        )(layer_name, *da.rio.bounds(), *da.rio.resolution(), da.data[0])

        self.loaded_rasters[layer_name] = local_raster

        multi_band = False
        if len(da.band) > 1 and type(bands) != int:
            multi_band = True
            if not bands:
                bands = [3, 2, 1]
        elif len(da.band) == 1:
            bands = 1

        if multi_band:
            da = da.rio.write_nodata(0)
        else:
            da = da.rio.write_nodata(np.nan)
        da = da.sel(band=bands)

        kwargs = {
            "m": self,
            "x_dim": x_dim,
            "y_dim": y_dim,
            "fit_bounds": fit_bounds,
            "get_base_url": get_base_url,
            # 'colorbar_position': colorbar_position, # will be uncoment when the colobared version of xarray-leaflet will be released
            "rgb_dim": "band" if multi_band else None,
            "colormap": None if multi_band else colormap,
        }

        # display the layer on the map
        layer = da.leaflet.plot(**kwargs)

        layer.name = layer_name

        layer.opacity = opacity if abs(opacity) <= 1.0 else 1.0

        return

    def show_dc(self):
        """
        show the drawing control on the map

        Return:
            self
        """

        if self.dc:
            self.dc.clear()

            if self.dc not in self.controls:
                self.add_control(self.dc)

        return self

    def hide_dc(self):
        """
        hide the drawing control of the map

        Return:
            self
        """

        if self.dc:
            self.dc.clear()

            if self.dc in self.controls:
                self.remove_control(self.dc)

        return self

    def add_colorbar(
        self,
        colors,
        cmap="viridis",
        vmin=0,
        vmax=1.0,
        index=None,
        categorical=False,
        step=None,
        height="45px",
        transparent_bg=False,
        position="bottomright",
        layer_name=None,
        **kwargs,
    ):
        """Add a colorbar to the map.

        Args:
            colors (list, optional): The set of colors to be used for interpolation. Colors can be provided in the form: * tuples of RGBA ints between 0 and 255 (e.g: (255, 255, 0) or (255, 255, 0, 255)) * tuples of RGBA floats between 0. and 1. (e.g: (1.,1.,0.) or (1., 1., 0., 1.)) * HTML-like string (e.g: “#ffff00) * a color name or shortcut (e.g: “y” or “yellow”)
            cmap (str): a matplotlib colormap default to viridis
            vmin (int, optional): The minimal value for the colormap. Values lower than vmin will be bound directly to colors[0].. Defaults to 0.
            vmax (float, optional): The maximal value for the colormap. Values higher than vmax will be bound directly to colors[-1]. Defaults to 1.0.
            index (list, optional):The values corresponding to each color. It has to be sorted, and have the same length as colors. If None, a regular grid between vmin and vmax is created.. Defaults to None.
            categorical (bool, optional): Whether or not to create a categorical colormap. Defaults to False.
            step (int, optional): The step to split the LinearColormap into a StepColormap. Defaults to None.
            height (str, optional): The height of the colormap widget. Defaults to "45px".
            position (str, optional): The position for the colormap widget. Defaults to "bottomright".
            layer_name (str, optional): Layer name of the colorbar to be associated with. Defaults to None.
            kwargs (any): any other argument of the colorbar object from matplotlib
        """

        width, height = 6.0, 0.4

        alpha = 1

        if colors is not None:

            # transform colors in hex colors
            hexcodes = [su.to_colors(c) for c in colors]

            if categorical:
                cmap = mpc.ListedColormap(hexcodes)
                vals = np.linspace(vmin, vmax, cmap.N + 1)
                norm = mpc.BoundaryNorm(vals, cmap.N)

            else:
                cmap = mpc.LinearSegmentedColormap.from_list("custom", hexcodes, N=256)
                norm = mpc.Normalize(vmin=vmin, vmax=vmax)

        elif cmap is not None:

            cmap = plt.get_cmap(cmap)
            norm = mpc.Normalize(vmin=vmin, vmax=vmax)

        else:
            raise ValueError(
                'cmap keyword or "palette" key in vis_params must be provided.'
            )

        style = "dark_background" if v.theme.dark is True else "classic"

        with plt.style.context(style):
            fig, ax = plt.subplots(figsize=(width, height))
            cb = colorbar.ColorbarBase(
                ax,
                norm=norm,
                alpha=alpha,
                cmap=cmap,
                orientation="horizontal",
                **kwargs,
            )

            # cosmetic improvement
            cb.outline.set_visible(False)  # remove border of the color bar
            ax.tick_params(size=0)  # remove ticks
            fig.patch.set_alpha(0.0)  # remove bg of the fig
            ax.patch.set_alpha(0.0)  # remove bg of the ax

        if layer_name:
            cb.set_label(layer_name)

        output = widgets.Output()
        colormap_ctrl = ipyleaflet.WidgetControl(
            widget=output,
            position=position,
            transparent_bg=True,
        )
        with output:
            output.clear_output()
            plt.show()

        self.colorbar = colormap_ctrl
        if layer_name in self.ee_layer_names:
            if "colorbar" in self.ee_layer_dict[layer_name]:
                self.remove_control(self.ee_layer_dict[layer_name]["colorbar"])
            self.ee_layer_dict[layer_name]["colorbar"] = colormap_ctrl

        self.add_control(colormap_ctrl)

        return

    def addLayer(
        self,
        ee_object,
        vis_params={},
        name=None,
        shown=True,
        opacity=1.0,
        viz_name=False,
    ):
        """
        Override the addLayer method from geemap to read the guess the vizaulization parameters the same way as in SEPAL recipes.
        If the vizparams are empty and vizualization metadata exist, SepalMap will use them automatically.

        Args:
            ee_object (ee.Object): the ee OBject to draw on the map
            vis_params (dict, optional): the visualization parameters set as in GEE
            name (str, optional): the name of the layer
            shown (bool, optional): either to show the layer or not, default to true (it is bugged in ipyleaflet)
            opacity (float, optional): the opcity of the layer from 0 to 1, default to 1.
            viz_name (str, optional): the name of the vizaulization you want ot use. default to the first one if existing
        """

        # get the list of viz params
        viz = self.get_viz_params(ee_object)

        # get the requested vizparameters name
        # if non is set use the first one
        if not viz == {}:
            viz_name = viz_name or viz[next(iter(viz))]["name"]

        # apply it to vis_params
        if vis_params == {} and viz != {}:

            # find the viz params in the list
            try:
                vis_params = next(i for p, i in viz.items() if i["name"] == viz_name)
            except StopIteration:
                raise ValueError(
                    f"the provided viz_name ({viz_name}) cannot be found in the image metadata"
                )

            # invert the bands if needed
            inverted = vis_params.pop("inverted", None)
            if inverted is not None:

                # get the index of the bands taht need to be inverted
                index_list = [i for i, v in enumerate(inverted) if v is True]

                # multiply everything by -1
                for i in index_list:
                    min_ = vis_params["min"][i]
                    max_ = vis_params["max"][i]
                    vis_params["min"][i] = max_
                    vis_params["max"][i] = min_

            # specific case of categorical images
            # Pad the palette when using non-consecutive values
            # instead of remapping or using sldStyle
            # to preserve the class values in the image, for inspection
            if vis_params["type"] == "categorical":

                colors = vis_params["palette"]
                values = vis_params["values"]
                min_ = min(values)
                max_ = max(values)

                # set up a black palette of correct length
                palette = ["#000000"] * (max_ - min_ + 1)

                # replace the values within the palette
                for i, val in enumerate(values):
                    palette[val - min_] = colors[i]

                # adapt the vizparams
                vis_params["palette"] = palette
                vis_params["min"] = min_
                vis_params["max"] = max_

            # specific case of hsv
            elif vis_params["type"] == "hsv":

                # set to_min to 0 and to_max to 1
                # in the original expression:
                # 'to_min + (v - from_min) * (to_max - to_min) / (from_max - from_min)'
                expression = (
                    "{band} = (b('{band}') - {from_min}) / ({from_max} - {from_min})"
                )

                # get the maxs and mins
                # removing them from the parameter
                mins = vis_params.pop("min")
                maxs = vis_params.pop("max")

                # create the rgb bands
                asset = ee_object
                for i, band in enumerate(vis_params["bands"]):

                    # adapt the expression
                    exp = expression.format(
                        from_min=mins[i], from_max=maxs[i], band=band
                    )
                    asset = asset.addBands(asset.expression(exp), [band], True)

                # set the arguments
                ee_object = asset.select(vis_params["bands"]).hsvToRgb()
                vis_params["bands"] = ["red", "green", "blue"]

        # call the function using the replacing the empty viz params with the new one.
        super().addLayer(ee_object, vis_params, name, shown, opacity)

        return

    @staticmethod
    def get_basemap_list():
        """
        This function is intending for development use
        It give the list of all the available basemaps for SepalMap object

        Return:
            ([str]): the list of the basemap names
        """

        return [k for k in geemap.ee_basemaps.keys()]

    @staticmethod
    def get_viz_params(image):
        """
        Return the vizual parmaeters that are set in the metadata of the image

        Args:
            image (ee.Image): the image to analyse

        Return:
            (dict): the dictionnary of the find properties
        """

        # the constant prefix for SEPAL visualization parameters
        PREFIX = "visualization"

        # init the property list
        props = {}

        # check image type
        if not isinstance(image, ee.Image):
            return props

        # check that image have properties
        if "properties" not in image.getInfo():
            return props

        # build a raw prop list
        raw_prop_list = {
            p: val
            for p, val in image.getInfo()["properties"].items()
            if p.startswith(PREFIX)
        }

        # decompose each property by its number
        # and gather the properties in a sub dictionnary
        for p, val in raw_prop_list.items():

            # extract the number and create the sub-dict
            _, number, name = p.split("_")
            props[number] = props.pop(number, {})

            # modify the values according to prop key
            if isinstance(val, str):
                if name in ["bands", "palette", "labels"]:
                    val = val.split(",")
                elif name in ["max", "min", "values"]:
                    val = [float(i) for i in val.split(",")]
                elif name in ["inverted"]:
                    val = [bool(strtobool(i)) for i in val.split(",")]

            # set the value
            props[number][name] = val

        # categorical values need to be cast to int
        for i in props.keys():
            if props[i]["type"] == "categorical":
                props[i]["values"] = [int(val) for val in props[i]["values"]]

        return props
