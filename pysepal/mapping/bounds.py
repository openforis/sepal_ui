"""Auxiliary functions for computing map bounds and zoom levels."""

import math

from pyproj import Transformer


def compute_center(bounds):
    """Given [[south, west], [north, east]], return (lat, lon) center."""
    (south, west), (north, east) = bounds
    return ((south + north) / 2, (west + east) / 2)


_MERCATOR_MAX_LAT = 85.05112878


def _mercator_y_px(lat, world_px):
    """Return Web Mercator Y pixel coordinate at the given world pixel size."""
    lat = max(-_MERCATOR_MAX_LAT, min(_MERCATOR_MAX_LAT, lat))
    lat_rad = math.radians(lat)
    return world_px * (0.5 - math.log(math.tan(math.pi / 4 + lat_rad / 2)) / (2 * math.pi))


def viewport_pixels_from_map(map_widget):
    """Derive the map viewport (width, height) in pixels from synced bounds+zoom.

    Longitude is linear in Web Mercator pixels (360° == ``256 * 2**zoom``),
    so the east-west bounds span gives width directly. Latitude is non-linear
    (Mercator stretches toward the poles), so height is computed via the
    Mercator Y formula.

    Returns ``(None, None)`` if bounds/zoom are not yet available.
    """
    bounds = getattr(map_widget, "bounds", None)
    zoom = getattr(map_widget, "zoom", None)
    if not bounds or zoom is None:
        return None, None
    try:
        (south, west), (north, east) = bounds
    except (TypeError, ValueError):
        return None, None
    world_px = 256 * (2**zoom)
    span_lon = (east - west) % 360 or 360
    width = span_lon * world_px / 360
    height = abs(_mercator_y_px(north, world_px) - _mercator_y_px(south, world_px))
    return (width if width > 0 else None, height if height > 0 else None)


def viewport_width_from_map(map_widget):
    """Back-compat wrapper returning only the viewport width in pixels."""
    return viewport_pixels_from_map(map_widget)[0]


def compute_zoom_for_bounds(
    bounds, map_width_px=1024, map_height_px=None, min_zoom=None, max_zoom=None
):
    """Calculate the Web Mercator zoom that fits `bounds` into the viewport.

    If ``map_height_px`` is provided, the zoom is limited by whichever axis
    runs out of pixels first (so tall bounds in a wide viewport, or vice
    versa, still fit fully). If omitted, behaviour matches the previous
    width-only calculation.
    """
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    (south, west), (north, east) = bounds
    min_x, min_y = transformer.transform(west, south)
    max_x, max_y = transformer.transform(east, north)

    # Determine span in meters
    span_x = abs(max_x - min_x)
    span_y = abs(max_y - min_y)

    if span_x == 0 and span_y == 0:
        # Return the maximum zoom level for a point
        zoom = max_zoom if max_zoom is not None else 18
        return zoom

    # meters per pixel needed to fit each axis; the larger one is the limit
    res_x = span_x / map_width_px if map_width_px > 0 else float("inf")
    if map_height_px and map_height_px > 0:
        res_y = span_y / map_height_px
    else:
        # Fallback: treat viewport as square (legacy behaviour)
        res_y = span_y / map_width_px if map_width_px > 0 else float("inf")
    resolution = max(res_x, res_y)

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
