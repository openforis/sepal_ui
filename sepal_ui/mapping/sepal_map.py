"""The customized ``Map`` object."""

# known bug of rasterio
import os

from sepal_ui.mapping.bounds import (
    compute_center,
    compute_zoom_for_bounds,
)
from sepal_ui.mapping.fullscreen_control import FullScreenControl
from sepal_ui.mapping.visualization import get_viz_params, get_viz_params_async
from sepal_ui.scripts.gee_interface import GEEInterface
from sepal_ui.sepalwidgets.vue_app import ThemeToggle

if "GDAL_DATA" in list(os.environ.keys()):
    del os.environ["GDAL_DATA"]
if "PROJ_LIB" in list(os.environ.keys()):
    del os.environ["PROJ_LIB"]

import json
import math
import random
import string
from pathlib import Path
from typing import List, Optional, Sequence, Union, cast

import ee
import ipyleaflet as ipl
import ipyvuetify as v
import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import rioxarray
from deprecated.sphinx import deprecated
from eeclient.client import EESession
from ipyleaflet import TileLayer  # noqa: F401 - leave it here, it is used in the eval
from localtileserver import TileClient, get_leaflet_tile_layer
from matplotlib import colorbar
from matplotlib import colors as mpc
from rasterio.crs import CRS
from typing_extensions import Self

from sepal_ui import color as scolors
from sepal_ui import sepalwidgets as sw
from sepal_ui.frontend import styles as ss
from sepal_ui.mapping.basemaps import basemap_tiles
from sepal_ui.mapping.draw_control import DrawControl
from sepal_ui.mapping.inspector_control import InspectorControl
from sepal_ui.mapping.layer import EELayer
from sepal_ui.mapping.layer_state_control import LayerStateControl
from sepal_ui.mapping.layers_control import LayersControl
from sepal_ui.mapping.legend_control import LegendControl
from sepal_ui.mapping.zoom_control import ZoomControl
from sepal_ui.message import ms
from sepal_ui.scripts import decorator as sd
from sepal_ui.scripts import utils as su

__all__ = ["SepalMap"]

import logging

log = logging.getLogger("sepalui.mapping")


class SepalMap(ipl.Map):
    # ##########################################################################
    # ###                              Map parameters                        ###
    # ##########################################################################

    gee: bool = True
    "Either the map will use ee binding or not"

    v_inspector: Optional[InspectorControl] = None
    "The value inspector of the map"

    dc: Optional[DrawControl] = None
    "The drawing control of the map"

    _id: str = ""
    "A unique 6 letters str to identify the map in the DOM"

    state: Optional[sw.StateBar] = None
    "The statebar to inform the user about tile loading"

    def __init__(
        self,
        basemaps: List[str] = [],
        dc: bool = False,
        vinspector: bool = False,
        gee: bool = True,
        statebar: bool = False,
        theme_toggle: ThemeToggle = None,
        gee_session: Optional[EESession] = None,
        gee_interface: Optional[GEEInterface] = None,
        fullscreen: bool = False,
        map_id: str = "",
        **kwargs,
    ) -> None:
        """Custom Map object design to build application.

        The SepalMap class inherits from ipyleaflet.Map. It can thus be initialized with all its parameter.
        The map will fall back to CartoDB.DarkMatter map that well fits with the rest of the sepal_ui layout.
        Numerous methods have been added in the class to help you deal with your workflow implementation.
        It can natively display raster from .tif files and files and ee objects using methods
        that have the same signature as the GEE JavaScripts console.

        Args:
            basemaps: the basemaps used as background in the map. If multiple selection, they will be displayed as layers.
            dc: whether or not the drawing control should be displayed. default to false
            vinspector: Add value inspector to map, useful to inspect pixel values. default to false
            gee: whether or not to use the ee binding. If False none of the earthengine display functionalities can be used. default to True
            statebar: whether or not to display the Statebar in the map
            theme_toggle: sepal_ui ThemeToggle object
            gee_session (optional): a custom EESession object to do gee requests. default to None (deprecated in favor of gee_interface)
            gee_interface: a shared GEEInterface instance. If provided, takes precedence over gee_session
            fullscreen: whether or not to display the map in full screen. default to False
            kwargs (optional): any parameter from a ipyleaflet.Map. if set, 'ee_initialize' will be overwritten.

        Raises:
            ValueError: if both gee_session and gee_interface are provided

        .. versionadded:: 3.0.0
            Added gee_interface parameter for sharing GEEInterface instances across components.
        """
        # Validate input parameters
        if gee_session and gee_interface:
            raise ValueError(
                "Cannot provide both gee_session and gee_interface. "
                "Use gee_interface for shared instances or gee_session for component-specific sessions."
            )

        log.debug(
            f"Map initialization with gee: {gee} and session: {gee_session} and interface: {gee_interface} ID: {id(gee_interface)}"
        )

        # set the default parameters
        kwargs.setdefault("center", [0, 0])
        kwargs.setdefault("zoom", 2)
        kwargs.setdefault("max_zoom", 24)
        kwargs["basemap"] = {}
        kwargs["zoom_control"] = False
        kwargs["attribution_control"] = False
        kwargs["scroll_wheel_zoom"] = True
        kwargs.setdefault("world_copy_jump", True)

        if fullscreen:
            self.add_class("full-screen-map")

        super().__init__(**kwargs)

        # init ee
        self.gee = gee
        if gee:
            if gee_interface:
                self.gee_interface = gee_interface
            else:
                self.gee_interface = GEEInterface(session=gee_session)
            su.init_ee()

        # add the basemaps
        self.clear()
        if theme_toggle:
            default_basemap = "CartoDB.DarkMatter" if theme_toggle.dark else "CartoDB.Positron"
            theme_toggle.observe(self._on_theme_change, "dark")
            log.debug(f"Using solara theme: {theme_toggle.dark}")
        else:
            default_basemap = "CartoDB.DarkMatter" if v.theme.dark is True else "CartoDB.Positron"
            v.theme.observe(self._on_theme_change, "dark")

        basemaps = basemaps or [default_basemap]
        [self.add_basemap(basemap) for basemap in set(basemaps)]

        # set the visibility of all the basemaps to False but the first one
        [setattr(lyr, "visible", False) for lyr in self.layers]
        self.layers[0].visible = True

        # add the base controls
        self.add(ZoomControl(self))
        self.add(LayersControl(self, group=-1))
        self.add(ipl.AttributionControl(position="bottomleft", prefix="SEPAL"))
        self.add(ipl.ScaleControl(position="bottomleft", imperial=False))

        if kwargs.get("fullscreen_control", False):
            self.add(FullScreenControl(self))

        # specific drawing control
        self.dc = DrawControl(self)
        not dc or self.add(self.dc)

        # specific v_inspector
        self.v_inspector = InspectorControl(self)
        not vinspector or self.add(self.v_inspector)

        # specific statebar
        self.state = LayerStateControl(self)
        not statebar or self.add(self.state)

        # create a proxy ID to the element
        # this id should be unique and will be used by mutators to identify this map
        self._id = map_id or "".join(random.choice(string.ascii_lowercase) for i in range(6))
        self.add_class(self._id)

    def _on_theme_change(self, change) -> None:
        """Change the basemap layer."""
        # This is the way to make it work in solara do not ask me why
        light = eval(str(basemap_tiles["CartoDB.Positron"]))
        dark = eval(str(basemap_tiles["CartoDB.DarkMatter"]))

        layer_names = [layer.name for layer in self.layers]

        if change["new"]:
            if light.name in layer_names:
                idx = layer_names.index(light.name)
                layer = self.layers[idx]
                self.remove_layer(layer, base=True, none_ok=True)
                self.layers = self.layers[:idx] + (dark,) + self.layers[idx:]
        else:
            if dark.name in layer_names:
                idx = layer_names.index(dark.name)
                layer = self.layers[idx]
                self.remove_layer(layer, base=True, none_ok=True)
                self.layers = self.layers[:idx] + (light,) + self.layers[idx:]

    @deprecated(version="2.8.0", reason="the local_layer stored list has been dropped")
    def _remove_local_raster(self, local_layer: str) -> Self:
        """Remove local layer from memory.

        .. danger::

            Does nothing now.

        Args:
            local_layer (str | ipyleaflet.TileLayer): The local layer to remove or its name
        """
        return self

    @deprecated(version="2.8.0", reason="use remove_layer(-1) instead")
    def remove_last_layer(self, local: bool = False) -> Self:
        """Remove last added layer from Map.

        Args:
            local: Specify True to only remove local last layers, otherwise will remove every last layer.
        """
        self.remove_layer(-1)

        return self

    def set_center(self, lon: float, lat: float, zoom: int = -1) -> None:
        """Centers the map view at a given coordinates with the given zoom level.

        Args:
            lon: The longitude of the center, in degrees.
            lat: The latitude of the center, in degrees.
            zoom: The zoom level, from 1 to 24. Defaults to None.
        """
        self.center = [lat, lon]
        self.zoom = self.zoom if zoom == -1 else zoom

        return

    @sd.need_ee
    def zoom_ee_object(self, item: ee.ComputedObject, zoom_out: int = 1) -> Self:
        """Get the proper zoom to the given ee geometry.

        Args:
            item: the geometry to zoom on
            zoom_out: Zoom out the bounding zoom
        """
        # type check the given object
        ee_geometry = item if isinstance(item, ee.Geometry) else item.geometry()

        # extract bounds from ee_object
        coords = self.gee_interface.get_info(ee_geometry.bounds().coordinates().get(0))

        # zoom on these bounds
        return self.zoom_bounds((*coords[0], *coords[2]), zoom_out)

    def zoom_raster(self, layer: ipl.LocalTileLayer, zoom_out: int = 1) -> Self:
        """Adapt the zoom to the given LocalLayer.

        The localLayer need to come from the add_raster method to embed the image name.

        Args:
            layer: the localTile layer to zoom on. it needs to embed the "raster" member
            zoom_out: Zoom out the bounding zoom
        """
        da = rioxarray.open_rasterio(layer.raster, masked=True)

        # unproject if necessary
        epsg_4326 = "EPSG:4326"
        if da.rio.crs != CRS.from_string(epsg_4326):
            da = da.rio.reproject(epsg_4326)

        return self.zoom_bounds(da.rio.bounds(), zoom_out)

    def zoom_bounds(self, bounds: Sequence[float], zoom_out: int = 1) -> Self:
        """Adapt the zoom to the given bounds. and center the image.

        Args:
            bounds: coordinates corners as minx, miny, maxx, maxy in EPSG:4326
            zoom_out: Zoom out the bounding zoom
        """
        # center the map
        minx, miny, maxx, maxy = bounds
        self.fit_bounds([[miny, minx], [maxy, maxx]])

        # adapt the zoom level
        zoom_out = (self.zoom - 1) if zoom_out > self.zoom else zoom_out

        self.zoom -= zoom_out

        return self

    def add_raster(
        self,
        image: Union[str, Path],
        bands: Optional[Union[list, int]] = None,
        layer_name: str = "Layer_" + su.random_string(),
        colormap: Union[str, mpc.Colormap] = "inferno",
        opacity: float = 1.0,
        fit_bounds: bool = True,
        key: str = "",
    ) -> ipl.TileLayer:
        """Adds a local raster dataset to the map.

        If used on a cloud platform (or distant jupyter), this method won't know where the entry point of the client is set and will thus fail to display the image. Please follow instructions from https://localtileserver.banesullivan.com/installation/remote-jupyter.html and set up the ``LOCALTILESERVER_CLIENT_PREFIX`` environment variable.

        Args:
            image: The image file path.
            bands: The image bands to use. It can be either a number (e.g., 1) or a list (e.g., [3, 2, 1]). Defaults to None.
            layer_name: The layer name to use for the raster. Defaults to None. If a layer is already using this name 3 random letter will be added
            colormap: The name of the colormap to use for the raster, such as 'gray' and 'terrain'. More can be found at https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html. Defaults to inferno.
            opacity: the opacity of the layer, default 1.0.
            key: the unequivocal key of the layer. by default use a normalized str of the layer name
            fit_bounds: Whether or not we should fit the map to the image bounds. Default to True.

        Returns:
            the local tile layer embedding the raster member (to be used with other tools of sepal-ui)
        """
        # force cast to Path and then start the client
        image = Path(image)

        if not image.is_file():
            raise Exception(ms.mapping.no_image)

        client = TileClient(image)

        # check inputs
        if layer_name in [layer.name for layer in self.layers]:
            layer_name = layer_name + su.random_string()

        # set the colors as independent colors
        if isinstance(colormap, str):
            cmap = plt.get_cmap(name=colormap)
        color_list = [mpc.rgb2hex(cmap(i)) for i in range(cmap.N)]

        da = rioxarray.open_rasterio(image, masked=True)
        # print
        print(da)
        da = da.chunk({"x": 1000, "y": 1000})

        multi_band = False
        if len(da.band) > 1 and not isinstance(bands, int):
            multi_band = True
            bands = bands if bands else [3, 2, 1]
        elif len(da.band) == 1:
            bands = 1

        if multi_band:
            cast(list, bands)
            style = {
                "bands": [
                    {"band": bands[0], "palette": "#f00"},
                    {"band": bands[1], "palette": "#0f0"},
                    {"band": bands[2], "palette": "#00f"},
                ]
            }
        else:
            style = {
                "bands": [
                    {"band": bands, "palette": color_list},
                ]
            }

        # create the layer
        layer = get_leaflet_tile_layer(
            client,
            style=style,
            name=layer_name,
            opacity=opacity,
            max_zoom=20,
            max_native_zoom=20,
        )
        self.add_layer(layer, key=key)

        # add the da to the layer as an extra member for the v_inspector
        layer.raster = str(image)

        # zoom on the layer if requested
        if fit_bounds is True:
            self.center = client.center()
            self.zoom = client.default_zoom

        return layer

    def add_colorbar(
        self,
        colors: list,
        cmap: str = "viridis",
        vmin: float = 0.0,
        vmax: float = 1.0,
        index: list = [],
        categorical: bool = False,
        step: int = 0,
        transparent_bg: bool = False,
        position: str = "bottomright",
        layer_name: str = "",
        **kwargs,
    ) -> None:
        """Add a colorbar to the map.

        Args:
            colors: The set of colors to be used for interpolation. Colors can be provided in the form: * tuples of RGBA ints between 0 and 255 (e.g: (255, 255, 0) or (255, 255, 0, 255)) * tuples of RGBA floats between 0. and 1. (e.g: (1.,1.,0.) or (1., 1., 0., 1.)) * HTML-like string (e.g: “#ffff00) * a color name or shortcut (e.g: “y” or “yellow”)
            cmap: a matplotlib colormap default to viridis
            vmin: The minimal value for the colormap. Values lower than vmin will be bound directly to colors[0].. Defaults to 0.
            vmax: The maximal value for the colormap. Values higher than vmax will be bound directly to colors[-1]. Defaults to 1.0.
            index: The values corresponding to each color. It has to be sorted, and have the same length as colors. If None, a regular grid between vmin and vmax is created. Defaults to None.
            categorical (bool, optional): Whether or not to create a categorical colormap. Defaults to False.
            step: The step to split the LinearColormap into a StepColormap. Defaults to None.
            position: The position for the colormap widget. Defaults to "bottomright".
            layer_name: Layer name of the colorbar to be associated with. Defaults to None.
            kwargs: any other argument of the colorbar object from matplotlib
        """
        width, height = 6.0, 0.4
        alpha = 1

        if colors is not None:
            # transform colors in hex colors
            hexcodes = [su.to_colors(c) for c in colors]

            if categorical:
                plot_color = mpc.ListedColormap(hexcodes)
                vals = np.linspace(vmin, vmax, plot_color.N + 1)
                norm = mpc.BoundaryNorm(vals, plot_color.N)

            else:
                plot_color = mpc.LinearSegmentedColormap.from_list("custom", hexcodes, N=256)
                norm = mpc.Normalize(vmin=vmin, vmax=vmax)

        elif cmap is not None:
            plot_color = plt.get_cmap(cmap)
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
                cmap=plot_color,
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

        self.add(colormap_ctrl)

        return

    def add_ee_layer(
        self,
        ee_object: ee.ComputedObject,
        vis_params: dict = {},
        name: str = "",
        shown: bool = True,
        opacity: float = 1.0,
        viz_name: str = "",
        key: str = "",
        use_map_vis: bool = True,
        autocenter: bool = False,
    ) -> None:
        """Customized add_layer method designed for EE objects.

        Copy the addLayer method from geemap to read and guess the vizaulization
        parameters the same way as in SEPAL recipes.
        If the vizparams are empty and visualization metadata exist, SepalMap will use
        them automatically.

        Args:
            ee_object: the ee OBject to draw on the map
            vis_params: the visualization parameters set as in GEE
            name: the name of the layer
            shown: either to show the layer or not, default to true (it is bugged in ipyleaflet)
            opacity: the opcity of the layer from 0 to 1, default to 1.
            viz_name: the name of the vizaulization you want to use. default to the first one if existing
            key: the unequivocal key of the layer. by default use a normalized str of the layer name
            use_map_vis: whether or not to use the map visualization parameters. default to True
            autocenter: whether or not to center the map on the layer. default to False
        """
        # get the visualization parameters
        image, obj, vis_params = get_viz_params(
            self.gee_interface,
            ee_object,
            vis_params=vis_params,
            viz_name=viz_name,
            use_map_vis=use_map_vis,
        )

        # create the layer based on these new values
        if not name:
            layer_count = len(self.layers)
            name = "Layer " + str(layer_count + 1)

        # create the colored image
        map_id_dict = self.gee_interface.get_map_id(image, vis_params)
        tile_layer = EELayer(
            ee_object=obj,
            url=map_id_dict["tile_fetcher"].url_format,
            attribution="Google Earth Engine",
            name=name,
            opacity=opacity,
            visible=shown,
            max_zoom=24,
        )

        if autocenter:
            bounds = self.gee_interface.get_info(ee_object.bounds().coordinates().get(0))
            self.zoom_bounds((*bounds[0], *bounds[2]))

        self.add_layer(tile_layer, key=key)

        return

    async def add_ee_layer_async(
        self,
        ee_object: ee.ComputedObject,
        vis_params: dict = {},
        name: str = "",
        shown: bool = True,
        opacity: float = 1.0,
        viz_name: str = "",
        key: str = "",
        use_map_vis: bool = True,
    ) -> None:
        """Customized add_layer method designed for EE objects.

        Copy the addLayer method from geemap to read and guess the vizaulization
        parameters the same way as in SEPAL recipes.
        If the vizparams are empty and visualization metadata exist, SepalMap will use
        them automatically.

        Args:
            ee_object: the ee OBject to draw on the map
            vis_params: the visualization parameters set as in GEE
            name: the name of the layer
            shown: either to show the layer or not, default to true (it is bugged in ipyleaflet)
            opacity: the opcity of the layer from 0 to 1, default to 1.
            viz_name: the name of the vizaulization you want to use. default to the first one if existing
            key: the unequivocal key of the layer. by default use a normalized str of the layer name
            use_map_vis: whether or not to use the map visualization parameters. default to True
        """
        # get the visualization parameters
        image, obj, vis_params = await get_viz_params_async(
            self.gee_interface,
            ee_object,
            vis_params=vis_params,
            viz_name=viz_name,
            use_map_vis=use_map_vis,
        )

        # create the layer based on these new values
        if not name:
            layer_count = len(self.layers)
            name = "Layer " + str(layer_count + 1)

        # create the colored image
        map_id_dict = await self.gee_interface.get_map_id_async(image, vis_params)
        tile_layer = EELayer(
            ee_object=obj,
            url=map_id_dict["tile_fetcher"].url_format,
            attribution="Google Earth Engine",
            name=name,
            opacity=opacity,
            visible=shown,
            max_zoom=24,
        )

        self.add_layer(tile_layer, key=key)

        return

    @staticmethod
    def get_basemap_list() -> List[str]:
        """Get the complete list of available basemaps.

        This function is intending for development use
        It give the list of all the available basemaps for SepalMap object.

        Returns:
            The list of the basemap names
        """
        return [k for k in basemap_tiles.keys()]

    def remove_layer(
        self, key: Union[ipl.Layer, int, str], base: bool = False, none_ok: bool = False
    ) -> None:
        """Remove a layer based on a key.

        The key can be, a Layer object, the name of a layer or the index in the layer list.

        Args:
            key: the key to find the layer to delete
            base: either the basemaps should be included in the search or not. default t false
            none_ok: if True the function will not raise error if no layer is found. Default to False
        """
        layer = self.find_layer(key, base, none_ok)

        # the error is caught in find_layer
        if layer is not None:
            super().remove(layer)

        return

    def remove_all(self, base: bool = False, keep_names: Optional[list[str]] = None) -> None:
        """Remove all the layers from the maps.

        If base is set to True, the basemaps are removed as well.

        Args:
            base: whether or not the basemaps should be removed, default to False
            keep_names: if set, will keep the layers with these names
        """
        # filter out the basemaps if base == False
        layers = self.layers if base else [lyr for lyr in self.layers if not lyr.base]

        # remove them using the layer objects as keys
        [
            self.remove_layer(layer, base)
            for layer in layers
            if not keep_names or layer.name not in keep_names
        ]

        return

    def add_layer(self, layer: ipl.Layer, hover: bool = False, key: str = "") -> None:
        """Add layer and use a default style for the GeoJSON inputs.

        Remove existing layer if already on the map.

        Args:
            layer: any layer type from ipyleaflet
            hover: whether to use the default hover style or not.
            key: the unequivocal key of the layer. by default use a normalized str of the layer name
        """
        # set up a unique key
        layer.key = key if key else su.normalize_str(layer.name)

        # remove existing layer before addition
        existing_layer = self.find_layer(layer.key, none_ok=True)
        not existing_layer or self.remove_layer(existing_layer)

        # apply default coloring for geoJson
        if isinstance(layer, ipl.GeoJSON):
            # define the default values
            default_style = json.loads((ss.JSON_DIR / "layer.json").read_text())["layer"]
            default_style.update(color=scolors.primary)
            default_hover_style = json.loads((ss.JSON_DIR / "layer_hover.json").read_text())
            default_hover_style.update(color=scolors.primary)

            # apply the style depending on the parameters
            layer.style = layer.style or default_style
            hover_style = default_hover_style if hover else layer.hover_style
            layer.hover_style = layer.hover_style or hover_style

        super().add(layer)

        return

    def add_basemap(self, basemap: str = "HYBRID") -> None:
        """Adds a basemap to the map.

        Args:
            basemap: Can be one of string from basemaps. Defaults to 'HYBRID'.
        """
        if basemap not in basemap_tiles.keys():
            keys = "\n".join(basemap_tiles.keys())
            msg = f"Basemap can only be one of the following:\n{keys}"
            raise ValueError(msg)

        self.add_layer(eval(str(basemap_tiles[basemap])))

        return

    def get_scale(self) -> float:
        """Returns the approximate pixel scale of the current map view, in meters.

        Reference: https://blogs.bing.com/maps/2006/02/25/map-control-zoom-levels-gt-resolution.

        Returns:
            Map resolution in meters.
        """
        return 156543.04 * math.cos(0) / math.pow(2, self.zoom)

    def find_layer(
        self, key: Union[ipl.Layer, str, int], base: bool = False, none_ok: bool = False
    ) -> ipl.TileLayer:
        """Search a layer by name or index.

        Args:
            key: the layer name, the layer key, the index or directly the layer
            base: either the basemaps should be included in the search or not. default to false
            none_ok: if True the function will not raise error if no layer is found. Default to False

        Returns:
            The first layer using the same name or index else None
        """
        # filter the layers
        layers = self.layers if base else [lyr for lyr in self.layers if not lyr.base]

        if isinstance(key, str):
            layer = next((lyr for lyr in layers if lyr.key == key), None)
            layer = layer or next((lyr for lyr in layers if lyr.name == key), None)
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

    def fit_bounds(self, bounds):
        """Abstract method to fit the map to the given bounds."""
        # I've done this because the native ipyleaflet fit bounds method uses
        # awaitables that create conflicts with solara.
        # Also I don't like the way it zooms by levels

        center = compute_center(bounds)
        self.center = center

        # 2) Determine map width in pixels
        width = None
        log.debug(f"getting map width from layout: {self.layout}")
        if hasattr(self, "layout"):
            width = getattr(self.layout, "width", None)
            log.debug(f"map width from layout: {width}")
        try:
            log.debug(f"getting map width from width: {width}")
            map_width_px = int(width)
        except (TypeError, ValueError) as e:
            log.debug(f"Error: {width}, {e}")
            map_width_px = 1024

        log.debug(f"map width in pixels: {map_width_px}")

        zoom = (
            compute_zoom_for_bounds(
                bounds,
                map_width_px,
                min_zoom=getattr(self, "min_zoom", None),
                max_zoom=getattr(self, "max_zoom", None),
            )
            + 1
        )
        self.zoom = zoom

    def add_legend(
        self,
        title: str = ms.mapping.legend,
        legend_dict: dict = {},
        position: str = "bottomright",
        vertical: bool = True,
    ) -> None:
        """Creates and adds a custom legend as widget control to the map.

        Args:
            title: Title of the legend. Defaults to 'Legend'.
            legend_dict: dictionary with key as label name and value as color
            position: the position (corners) of the legend on the map
            vertical: vertical or horizoal position of the legend
        """
        # Define as class member so it can be accessed from outside.
        self.legend = LegendControl(legend_dict, title=title, vertical=vertical, position=position)

        return self.add(self.legend)

        # ##########################################################################
        # ###                overwrite geemap calls                              ###
        # ##########################################################################

    setCenter = set_center
    centerObject = zoom_ee_object
    addLayer = add_ee_layer
    getScale = get_scale
