"""Module to load basemaps from different providers."""

import os
from typing import Optional

from box import Box
from ipyleaflet import TileLayer
from xyzservices import TileProvider
from xyzservices import providers as xyz

# CARTO started watermarking its raster tiles when they are requested without an API
# key, so the background defaults point at a keyless provider. A deployment overrides
# them through the environment with full XYZ URL templates, which keeps any API key out
# of the published package.
LIGHT_BASEMAP_URL: str = os.getenv(
    "LIGHT_BASEMAP_URL",
    "https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
)
"URL template of the light background basemap."

DARK_BASEMAP_URL: str = os.getenv(
    "DARK_BASEMAP_URL",
    "https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
)
"URL template of the dark background basemap."

BASEMAP_ATTRIBUTION: str = os.getenv("BASEMAP_ATTRIBUTION", "Esri")
"Attribution of the background basemaps. Must match the provider the URLs point at."

xyz_tiles: dict = {
    "SEPAL_LIGHT": {
        "url": LIGHT_BASEMAP_URL,
        "attribution": BASEMAP_ATTRIBUTION,
        "name": "SEPAL Light",
    },
    "SEPAL_DARK": {
        "url": DARK_BASEMAP_URL,
        "attribution": BASEMAP_ATTRIBUTION,
        "name": "SEPAL Dark",
    },
    "OpenStreetMap": {
        "url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        "attribution": "OpenStreetMap",
        "name": "OpenStreetMap",
    },
    "ROADMAP": {
        "url": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        "attribution": "Google",
        "name": "Google Maps",
    },
    "SATELLITE": {
        "url": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        "attribution": "Google",
        "name": "Google Satellite",
    },
    "TERRAIN": {
        "url": "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
        "attribution": "Google",
        "name": "Google Terrain",
    },
    "HYBRID": {
        "url": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        "attribution": "Google",
        "name": "Google Satellite",
    },
}
"Custom XYZ tile services."


def get_xyz_dict(
    free_only: bool = True,
    _collection: Optional[dict] = None,
    _output: Optional[dict] = None,
) -> dict:
    """Returns a dictionary of xyz services.

    Args:
        free_only: Whether to return only free xyz tile services that do not require an access token.
        _collection: the collection to anylize (subset of :code:`xyz`)
        _output: the dict to use as an output (mutable object)

    Returns:
        A dictionary of xyz services.
    """
    # the 2 following lies avoid to display xyz descriptor in the method documentation
    # do not replace in the prototype default values
    _collection = xyz if _collection is None else _collection
    _output = {} if _output is None else _output

    for v in _collection.values():
        if isinstance(v, TileProvider):
            if not (v.requires_token() and free_only):
                _output[v.name] = v
        else:  # it's a Bunch
            get_xyz_dict(free_only, v, _output)

    return _output


def xyz_to_leaflet() -> dict:
    """Convert all available xyz tile services to ipyleaflet tile layers.

    Adapted from https://github.com/giswqs/geemap.

    Returns:
        A dictionary of ipyleaflet tile layers.
    """
    leaflet_dict = {}

    for key in xyz_tiles:
        name = xyz_tiles[key]["name"]
        url = xyz_tiles[key]["url"]
        attribution = xyz_tiles[key]["attribution"]
        leaflet_dict[key] = TileLayer(
            url=url, name=name, attribution=attribution, max_zoom=22, base=True
        )

    for item in get_xyz_dict().values():
        leaflet_dict[item.name] = TileLayer(
            url=item.build_url(),
            name=item.name,
            max_zoom=item.get("max_zoom", 22),
            attribution=item.attribution,
            base=True,
        )

    return leaflet_dict


basemap_tiles: Box = Box(xyz_to_leaflet(), frozen_box=True)
"the basemaps list as a box"
