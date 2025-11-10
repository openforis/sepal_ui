"""Auxiliary functions for computing map bounds and zoom levels."""

import math

from pyproj import Transformer


def compute_center(bounds):
    """Given [[south, west], [north, east]], return (lat, lon) center."""
    (south, west), (north, east) = bounds
    return ((south + north) / 2, (west + east) / 2)


def compute_zoom_for_bounds(bounds, map_width_px=1024, min_zoom=None, max_zoom=None):
    """Calculate the Web Mercator zoom level that fits `bounds` into `map_width_px` pixels."""
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    (south, west), (north, east) = bounds
    min_x, min_y = transformer.transform(west, south)
    max_x, max_y = transformer.transform(east, north)

    # Determine span in meters
    span_x = abs(max_x - min_x)
    span_y = abs(max_y - min_y)
    span = max(span_x, span_y)

    if span == 0:
        # Return the maximum zoom level for a point
        zoom = max_zoom if max_zoom is not None else 18
        return zoom

    # Compute meters per pixel
    resolution = span / map_width_px

    # Derive zoom: WORLD_SIZE / (tile_size * 2**zoom) = resolution
    WORLD_SIZE = 2 * math.pi * 6_378_137
    tile_size = 256
    zoom_float = math.log2(WORLD_SIZE / (tile_size * resolution))
    zoom = int(math.floor(zoom_float))

    # Clamp to allowed range
    if min_zoom is not None:
        zoom = max(min_zoom, zoom)
    if max_zoom is not None:
        zoom = min(max_zoom, zoom)
    return zoom
