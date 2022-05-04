import collections
import ipyleaflet
import xyzservices.providers as xyz


xyz_tiles = {
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
"(dict): Custom XYZ tile services."


def get_xyz_dict(free_only=True):
    """
    Returns a dictionary of xyz services.
    Adapted from https://github.com/giswqs/geemap

    Args:
        free_only (bool, optional): Whether to return only free xyz tile services that do not require an access token. Defaults to True.

    Returns:
        dict: A dictionary of xyz services.
    """

    xyz_dict = {}
    for item in xyz.values():
        try:
            name = item["name"]
            tile = eval("xyz." + name)
            if eval("xyz." + name + ".requires_token()"):
                if free_only:
                    pass
                else:
                    xyz_dict[name] = tile
            else:
                xyz_dict[name] = tile

        except Exception:
            for sub_item in item:
                name = item[sub_item]["name"]
                tile = eval("xyz." + name)
                if eval("xyz." + name + ".requires_token()"):
                    if free_only:
                        pass
                    else:
                        xyz_dict[name] = tile
                else:
                    xyz_dict[name] = tile

    xyz_dict = collections.OrderedDict(sorted(xyz_dict.items()))

    return xyz_dict


def xyz_to_leaflet():
    """
    Convert all available xyz tile services to ipyleaflet tile layers.
    adapted from https://github.com/giswqs/geemap

    Returns:
        dict: A dictionary of ipyleaflet tile layers.
    """
    leaflet_dict = {}

    for key in xyz_tiles:
        name = xyz_tiles[key]["name"]
        url = xyz_tiles[key]["url"]
        attribution = xyz_tiles[key]["attribution"]
        leaflet_dict[key] = ipyleaflet.TileLayer(
            url=url, name=name, attribution=attribution, max_zoom=22
        )

    xyz_dict = get_xyz_dict()
    for item in xyz_dict:
        name = xyz_dict[item].name
        url = xyz_dict[item].build_url()
        attribution = xyz_dict[item].attribution
        if "max_zoom" in xyz_dict[item].keys():
            max_zoom = xyz_dict[item]["max_zoom"]
        else:
            max_zoom = 22
        leaflet_dict[name] = ipyleaflet.TileLayer(
            url=url, name=name, max_zoom=max_zoom, attribution=attribution
        )

    return leaflet_dict
