import xyzservices.providers as xyz
from box import Box
from ipyleaflet import TileLayer
from xyzservices import TileProvider


class BasemapBox(Box):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        return ",\n".join(list(self.keys()))


xyz_tiles: dict = {
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


def get_xyz_dict(free_only: bool = True, _collection: dict = xyz, _output={}) -> dict:
    """
    Returns a dictionary of xyz services.

    Args:
        free_only: Whether to return only free xyz tile services that do not require an access token.
        _collection: the collection to anylize (subset of :code:`xyz`
        _output: the dict to use as an output (mutable object)

    Returns:
        dict: A dictionary of xyz services.
    """

    for v in _collection.values():
        if isinstance(v, TileProvider):
            if not (v.requires_token() and free_only):
                _output[v.name] = v
        else:  # it's a Bunch
            get_xyz_dict(free_only, v, _output)

    return _output


def xyz_to_leaflet() -> dict:
    """
    Convert all available xyz tile services to ipyleaflet tile layers.
    Adapted from https://github.com/giswqs/geemap

    Returns:
        dict: A dictionary of ipyleaflet tile layers.
    """
    leaflet_dict = {}

    for key in xyz_tiles:
        name = xyz_tiles[key]["name"]
        url = xyz_tiles[key]["url"]
        attribution = xyz_tiles[key]["attribution"]
        leaflet_dict[key] = TileLayer(
            url=url, name=name, attribution=attribution, max_zoom=22, base=True
        )

    for i, item in get_xyz_dict().items():
        leaflet_dict[item.name] = TileLayer(
            url=item.build_url(),
            name=item.name,
            max_zoom=item.get("max_zoom", 22),
            attribution=item.attribution,
            base=True,
        )

    return leaflet_dict


basemap_tiles: BasemapBox = BasemapBox(xyz_to_leaflet(), frozen_box=True)
"the basemaps list as a box"
