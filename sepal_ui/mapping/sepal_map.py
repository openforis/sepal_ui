# knwon bug of rasterio
import os

if "GDAL_DATA" in list(os.environ.keys()):
    del os.environ["GDAL_DATA"]
if "PROJ_LIB" in list(os.environ.keys()):
    del os.environ["PROJ_LIB"]

from pathlib import Path
from distutils.util import strtobool
import warnings
import math

from haversine import haversine
import numpy as np
import rioxarray
import xarray_leaflet
import matplotlib.pyplot as plt
from matplotlib import colors as mpc
from matplotlib import colorbar
import ipywidgets as widgets
from rasterio.crs import CRS
import ipyvuetify as v
import ipyleaflet as ipl
import ee
from deprecated.sphinx import deprecated

import sepal_ui.frontend.styles as styles
from sepal_ui.scripts import utils as su
from sepal_ui.scripts.warning import SepalWarning
from sepal_ui.message import ms
from sepal_ui.mapping.draw_control import DrawControl
from sepal_ui.mapping.value_inspector import ValueInspector
from sepal_ui.mapping.layer import EELayer
from sepal_ui.mapping.basemaps import basemap_tiles

__all__ = ["SepalMap"]

# call x_array leaflet at least once
# flake8 will complain as it's a pluggin (i.e. never called)
# We don't want to ignore testing F401
xarray_leaflet


class SepalMap(ipl.Map):
    """
    The SepalMap class inherits from ipyleaflet.Map. It can thus be initialized with all
    its parameter.
    The map will fall back to CartoDB.DarkMatter map that well fits with the rest of
    the sepal_ui layout.
    Numerous methods have been added in the class to help you deal with your workflow
    implementation.
    It can natively display raster from .tif files and files and ee objects using methods
    that have the same signature as the GEE JavaScripts console.

    Args:
        basemaps ['str']: the basemaps used as background in the map. If multiple selection, they will be displayed as layers.
        dc (bool, optional): wether or not the drawing control should be displayed. default to false
        vinspector (bool, optional): Add value inspector to map, useful to inspect pixel values. default to false
        gee (bool, optional): wether or not to use the ee binding. If False none of the earthengine display fonctionalities can be used. default to True
        kwargs (optional): any parameter from a ipyleaflet.Map. if set, 'ee_initialize' will be overwritten.
    """

    # ##########################################################################
    # ###                              Map parameters                        ###
    # ##########################################################################

    ee = True
    "bool: either the map will use ee binding or not"

    v_inspector = None
    "mapping.ValueInspector: the value inspector of the map"

    dc = None
    "ipyleaflet.DrawingControl: the drawing control of the map"

    def __init__(self, basemaps=[], dc=False, vinspector=False, gee=True, **kwargs):

        # set the default parameters
        kwargs["center"] = kwargs.pop("center", [0, 0])
        kwargs["zoom"] = kwargs.pop("zoom", 2)
        kwargs["basemap"] = {}
        kwargs["zoom_control"] = False
        kwargs["attribution_control"] = False
        kwargs["scroll_wheel_zoom"] = True
        kwargs["world_copy_jump"] = kwargs.pop("world_copy_jump", True)

        # Init the map
        super().__init__(**kwargs)

        # init ee
        self.ee = gee
        not gee or su.init_ee()

        # add the basemaps
        self.clear_layers()
        default_basemap = (
            "CartoDB.DarkMatter" if v.theme.dark is True else "CartoDB.Positron"
        )
        basemaps = basemaps or [default_basemap]
        [self.add_basemap(basemap) for basemap in set(basemaps)]

        # add the base controls
        self.add_control(ipl.ZoomControl(position="topright"))
        self.add_control(ipl.LayersControl(position="topright"))
        self.add_control(ipl.AttributionControl(position="bottomleft", prefix="SEPAL"))
        self.add_control(ipl.ScaleControl(position="bottomleft", imperial=False))

        # specific drawing control
        self.dc = DrawControl(self)
        not dc or self.add_control(self.dc)

        # specific v_inspector
        self.v_inspector = ValueInspector(self)
        not vinspector or self.add_control(self.v_inspector)

    @deprecated(version="2.8.0", reason="the local_layer stored list has been dropped")
    def _remove_local_raster(self, local_layer):
        """
        Remove local layer from memory.

        .. danger::

            Does nothing now.

        Args:
            local_layer (str | ipyleaflet.TileLayer): The local layer to remove or its name

        Return:
            self
        """

        return self

    @deprecated(version="2.8.0", reason="use remove_layer(-1) instead")
    def remove_last_layer(self, local=False):
        """
        Remove last added layer from Map

        Args:
            local (boolean): Specify True to only remove local last layers, otherwise will remove every last layer.

        Return:
            self
        """
        self.remove_layer(-1)

        return self

    def set_center(self, lon, lat, zoom=None):
        """
        Centers the map view at a given coordinates with the given zoom level.

        Args:
            lon (float): The longitude of the center, in degrees.
            lat	(float): The latitude of the center, in degrees.
            zoom (int|optional): The zoom level, from 1 to 24. Defaults to None.
        """

        self.center = [lat, lon]
        self.zoom = self.zoom if zoom is None else zoom

        return

    @su.need_ee
    def zoom_ee_object(self, item, zoom_out=1):
        """
        Get the proper zoom to the given ee geometry.

        Args:
            item (ee.ComputedObject): the geometry to zoom on
            zoom_out (int) (optional): Zoom out the bounding zoom

        Return:
            self
        """

        # type check the given object
        ee_geometry = item if isinstance(item, ee.Geometry) else item.geometry()

        # extract bounds from ee_object
        coords = ee_geometry.bounds().coordinates().get(0).getInfo()

        # zoom on these bounds
        self.zoom_bounds((*coords[0], *coords[2]), zoom_out)

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

        # create the tuples for each corner
        tl, br, bl, tr = (minx, maxy), (maxx, miny), (minx, miny), (maxx, maxy)

        # find zoom level to display the biggest diagonal (in km)
        lg, zoom = 40075, 1  # number of displayed km at zoom 1
        maxsize = max(haversine(tl, br), haversine(bl, tr))
        while lg > maxsize:
            (zoom, lg) = (zoom + 1, lg / 2)

        zoom_out = (zoom - 1) if zoom_out > zoom else zoom_out

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
        colorbar_position=False,
    ):
        """
        Adds a local raster dataset to the map.

        Args:
            image (str | pathlib.Path): The image file path.
            bands (int or list, optional): The image bands to use. It can be either a number (e.g., 1) or a list (e.g., [3, 2, 1]). Defaults to None.
            layer_name (str, optional): The layer name to use for the raster. Defaults to None. If a layer is already using this name 3 random letter will be added
            colormap (str, optional): The name of the colormap to use for the raster, such as 'gray' and 'terrain'. More can be found at https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html. Defaults to None.
            x_dim (str, optional): The x dimension. Defaults to 'x'.
            y_dim (str, optional): The y dimension. Defaults to 'y'.
            opacity (float, optional): the opacity of the layer, default 1.0.
            fit_bounds (bool, optional): Wether or not we should fit the map to the image bounds. Default to True.
            get_base_url (callable, optional): A function taking the window URL and returning the base URL to use. It's design to work in the SEPAL environment, you only need to change it if you want to work outside of our platform. See xarray-leaflet lib for more details.
            colorbar_position (str, optional): The position of the colorbar. By default set to False to remove it.
        """

        # force cast to Path
        image = Path(image)

        if not image.is_file():
            raise Exception(ms.mapping.no_image)

        # check inputs
        if layer_name in [layer.name for layer in self.layers]:
            layer_name = layer_name + su.random_string()

        if isinstance(colormap, str):
            colormap = plt.cm.get_cmap(name=colormap)

        da = rioxarray.open_rasterio(image, masked=True)

        # The dataset can be too big to hold in memory, so we will chunk it into smaller
        # pieces.
        # That will also improve performances as the generation of a tile can be done
        # in parallel using Dask.
        da = da.chunk((1000, 1000))

        # unproject if necessary
        epsg_4326 = "EPSG:4326"
        if da.rio.crs != CRS.from_string(epsg_4326):
            da = da.rio.reproject(epsg_4326)

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
            "colorbar_position": colorbar_position,
            "rgb_dim": "band" if multi_band else None,
            "colormap": None if multi_band else colormap,
        }

        # display the layer on the map
        layer = da.leaflet.plot(**kwargs)
        layer.name = layer_name
        layer.opacity = opacity if abs(opacity) <= 1.0 else 1.0

        # add the da to the layer as an extra member for the v_inspector
        layer.raster = str(image)

        return

    @deprecated(version="2.8.0", reason="use dc methods instead")
    def show_dc(self):
        """
        show the drawing control on the map
        """
        self.dc.show()
        return self

    @deprecated(version="2.8.0", reason="use dc methods instead")
    def hide_dc(self):
        """
        hide the drawing control of the map
        """
        self.dc.hide()
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
            msg = '"cmap" keyword or "colors" key must be provided.'
            raise ValueError(msg)

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

        not layer_name or cb.set_label(layer_name)

        output = widgets.Output()
        colormap_ctrl = ipl.WidgetControl(
            widget=output,
            position=position,
            transparent_bg=True,
        )
        with output:
            output.clear_output()
            plt.show()

        self.add_control(colormap_ctrl)

        return

    def add_ee_Layer(
        self,
        ee_object,
        vis_params={},
        name=None,
        shown=True,
        opacity=1.0,
        viz_name=False,
    ):
        """
        Copy the addLayer method from geemap to read and guess the vizaulization
        parameters the same way as in SEPAL recipes.
        If the vizparams are empty and vizualization metadata exist, SepalMap will use
        them automatically.

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

                # get the index of the bands that need to be inverted
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

        # create the layer based on these new values
        image = None

        if name is None:
            layer_count = len(self.layers)
            name = "Layer " + str(layer_count + 1)

        # check the type of the ee object and raise an error if it's not recognized
        if not isinstance(
            ee_object,
            (
                ee.Image,
                ee.ImageCollection,
                ee.FeatureCollection,
                ee.Feature,
                ee.Geometry,
            ),
        ):
            raise AttributeError(
                "\n\nThe image argument in 'addLayer' function must be an instance of "
                "one of ee.Image, ee.Geometry, ee.Feature or ee.FeatureCollection."
            )

        # force cast to featureCollection if needed
        if isinstance(
            ee_object,
            (
                ee.geometry.Geometry,
                ee.feature.Feature,
                ee.featurecollection.FeatureCollection,
            ),
        ):

            features = ee.FeatureCollection(ee_object)

            width = vis_params.pop("width", 2)
            color = vis_params.pop("color", "000000")

            const_image = ee.Image.constant(0.5)
            image_fill = features.style(fillColor=color).updateMask(const_image)
            image_outline = features.style(
                color=color, fillColor="00000000", width=width
            )

            image = image_fill.blend(image_outline)
            obj = features

        # use directly the ee object if Image
        elif isinstance(ee_object, ee.image.Image):
            image = obj = ee_object

        # use mosaicing if the ee_object is a ImageCollection
        elif isinstance(ee_object, ee.imagecollection.ImageCollection):
            image = obj = ee_object.mosaic()

        # create the colored image
        map_id_dict = ee.Image(image).getMapId(vis_params)
        tile_layer = EELayer(
            ee_object=obj,
            url=map_id_dict["tile_fetcher"].url_format,
            attribution="Google Earth Engine",
            name=name,
            opacity=opacity,
            visible=shown,
            max_zoom=24,
        )

        self.add_layer(tile_layer)

        return

    @staticmethod
    def get_basemap_list():
        """
        This function is intending for development use
        It give the list of all the available basemaps for SepalMap object
        Return:
            ([str]): the list of the basemap names
        """

        return [k for k in basemap_tiles.keys()]

    @staticmethod
    def get_viz_params(image):
        """
        Return the vizual parameters that are set in the metadata of the image

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

        for i in props.keys():
            if "type" in props[i]:
                # categorical values need to be cast to int
                if props[i]["type"] == "categorical":
                    props[i]["values"] = [int(val) for val in props[i]["values"]]
            else:
                # if no "type" is provided guess it from the different parameters gathered
                if len(props[i]["bands"]) == 1:
                    props[i]["type"] = "continuous"
                elif len(props[i]["bands"]) == 3:
                    props[i]["type"] = "rgb"
                else:
                    warnings.warn(
                        "the embed viz properties are incomplete or badly set, "
                        "please review our documentation",
                        SepalWarning,
                    )
                    props = {}

        return props

    def remove_layer(self, key, base=False, none_ok=False):
        """
        Remove a layer based on a key. The key can be, a Layer object, the name of a
        layer or the index in the layer list

        Args:
            key (Layer, int, str): the key to find the layer to delete
            base (bool, optional): either the basemaps should be included in the search or not. default t false
            none_ok (bool, optional): if True the function will not raise error if no layer is found. Default to False
        """

        layer = self.find_layer(key, base, none_ok)

        # catch if the layer doesn't exist
        if layer is None:
            raise ipl.LayerException(f"layer not on map: {key}")

        super().remove_layer(layer)

        return

    def remove_all(self, base=False):
        """
        Remove all the layers from the maps.
        If base is set to True, the basemaps are removed as well

        Args:
            base (bool, optional): wether or not the basemaps should be removed, default to False
        """
        # filter out the basemaps if base == False
        layers = self.layers if base else [lyr for lyr in self.layers if not lyr.base]

        # remove them using the layer objects as keys
        [self.remove_layer(layer, base) for layer in layers]

        return

    def add_layer(self, layer, hover=False):
        """
        Add layer and use a default style for the GeoJSON inputs.
        Remove existing layer if already on the map.

        layer (ipyleaflet.Layer): any layer type from ipyleaflet
        hover (bool): whether to use the default hover style or not.
        """

        # remove existing layer before addition
        existing_layer = self.find_layer(layer.name, none_ok=True)
        not existing_layer or self.remove_layer(existing_layer)

        # apply default coloring for geoJson
        if isinstance(layer, ipl.GeoJSON):
            layer.style = layer.style or styles.layer_style
            hover_style = styles.layer_hover_style if hover else layer.hover_style
            layer.hover_style = layer.hover_style or hover_style

        super().add_layer(layer)

        return

    def add_basemap(self, basemap="HYBRID"):
        """
        Adds a basemap to the map.

        Args:
            basemap (str, optional): Can be one of string from basemaps. Defaults to 'HYBRID'.
        """
        if basemap not in basemap_tiles.keys():
            keys = "\n".join(basemap_tiles.keys())
            msg = f"Basemap can only be one of the following:\n{keys}"
            raise ValueError(msg)

        self.add_layer(basemap_tiles[basemap])

        return

    def get_scale(self):
        """
        Returns the approximate pixel scale of the current map view, in meters.
        Reference: https://blogs.bing.com/maps/2006/02/25/map-control-zoom-levels-gt-resolution

        Returns:
            (float): Map resolution in meters.
        """

        return 156543.04 * math.cos(0) / math.pow(2, self.zoom)

    def find_layer(self, key, base=False, none_ok=False):
        """
        Search a layer by name or index

        Args:
            key (Layer, str, int): the layer name, index or directly the layer
            base (bool, optional): either the basemaps should be included in the search or not. default to false
            none_ok (bool, optional): if True the function will not raise error if no layer is found. Default to False

        Return:
            (TileLLayerayer): the first layer using the same name or index else None
        """

        # filter the layers
        layers = self.layers if base else [lyr for lyr in self.layers if not lyr.base]

        if isinstance(key, str):
            layer = next((lyr for lyr in layers if lyr.name == key), None)
        elif isinstance(key, int):
            size = len(layers)
            layer = layers[key] if -size <= key < size else None
        elif isinstance(key, ipl.Layer):
            layer = next((lyr for lyr in layers if lyr == key), None)
        else:
            raise ValueError(f"key must be a int or a str, {type(key)} given")

        if layer is None and none_ok is False:
            raise ValueError(f"no layer corresponding to {key} on the map")

        return layer

    # ##########################################################################
    # ###                overwrite geemap calls                              ###
    # ##########################################################################

    setCenter = set_center
    centerObject = zoom_ee_object
    addLayer = add_ee_Layer
    getScale = get_scale
