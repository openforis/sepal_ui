"""Pure processing functions for AOI selection.

This module provides stateless functions for AOI processing, separating
business logic from UI components. All functions are async-friendly and
return immutable dataclasses.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import geopandas as gpd
import pygadm
import pygaul
from deprecated.sphinx import versionadded

from sepal_ui.message import ms
from sepal_ui.scripts import utils as su

__all__ = [
    "AoiResult",
    "fetch_admin_items",
    "process_admin",
    "process_draw",
]

# Path to GAUL -> ISO-3 mapping file
GAUL_ISO_MAPPING: Path = Path(__file__).parents[2] / "data" / "gaul_iso.json"

# Simple in-process cache to avoid repeating expensive admin lookups.
# Keyed by (gee, level, parent_code).
_ADMIN_ITEMS_CACHE: Dict[tuple, List[Dict[str, str]]] = {}


@dataclass(frozen=True)
@versionadded(version="3.1", reason="Pure Solara AOI result dataclass")
class AoiResult:
    """Immutable result from AOI selection.

    This dataclass represents the output of any AOI selection method.
    It is designed to be immutable (frozen) for predictable state management.

    Attributes:
        method: Selection method used (e.g., "ADMIN0", "ADMIN1", "ADMIN2", "DRAW")
        name: Human-readable name for the AOI (e.g., "FRA_Île-de-France")
        gdf: GeoDataFrame with the geometry (None for GEE-only workflows)
        feature_collection: ee.FeatureCollection for GEE workflows (None otherwise)
        admin: Admin code for admin methods (None for other methods)
        gee: Whether this result was created with GEE binding

    Example:
        ```python
        result = await process_admin("ADMIN1", "FRA.1_1", gee=False)
        print(f"Selected: {result.name}")
        ```
    """

    method: str
    name: str
    gdf: Optional[gpd.GeoDataFrame] = field(default=None, repr=False)
    feature_collection: Optional[Any] = field(default=None, repr=False)  # ee.FeatureCollection
    admin: Optional[str] = None
    gee: bool = False


def fetch_admin_items(
    level: int,
    parent_code: str = "",
    gee: bool = True,
) -> List[Dict[str, str]]:
    """Fetch administrative region items for dropdown selection.

    Retrieves a list of administrative regions at the specified level,
    optionally filtered by a parent region code.

    Args:
        level: Administrative level (0, 1, or 2)
        parent_code: Parent admin code to filter results. Empty string for level 0.
        gee: If True, use GAUL 2015 (for Earth Engine). If False, use GADM.

    Returns:
        List of dicts with 'text' (display name) and 'value' (admin code) keys.

    Example:
        ```python
        # Get all countries
        countries = fetch_admin_items(level=0, gee=False)

        # Get regions within France
        regions = fetch_admin_items(level=1, parent_code="FRA", gee=False)
        ```
    """
    cache_key = (gee, level, parent_code or "")
    cached = _ADMIN_ITEMS_CACHE.get(cache_key)
    if cached is not None:
        return cached

    AdmNames = pygaul.AdmNames if gee else pygadm.Names
    df = AdmNames(admin=parent_code or None, content_level=level)
    df = df.sort_values(by=[df.columns[0]])

    # Format as item list for select component
    item_list = []
    for _, r in df.iterrows():
        text = su.normalize_str(r.iloc[0], folder=False)
        item_list.append({"text": text, "value": str(r.iloc[1])})

    _ADMIN_ITEMS_CACHE[cache_key] = item_list
    return item_list


async def process_admin(
    method: str,
    admin_code: str,
    gee: bool = True,
    gee_interface: Optional[Any] = None,
) -> AoiResult:
    """Process administrative boundary selection.

    Fetches the geometry for the given administrative code using either
    GADM (local) or GAUL (Earth Engine).

    Args:
        method: The admin method ("ADMIN0", "ADMIN1", or "ADMIN2")
        admin_code: The administrative code to fetch
        gee: If True, use Earth Engine with GAUL. If False, use GADM locally.
        gee_interface: Optional GEEInterface for Earth Engine operations

    Returns:
        AoiResult with the administrative boundary data

    Raises:
        ValueError: If admin_code is empty or invalid

    Example:
        ```python
        # Select France (non-GEE)
        result = await process_admin("ADMIN0", "FRA", gee=False)

        # Select Île-de-France (GEE)
        result = await process_admin("ADMIN1", "75041", gee=True)
        ```
    """
    if not admin_code:
        raise ValueError(ms.aoi_sel.exception.no_admlyr)

    if method not in ["ADMIN0", "ADMIN1", "ADMIN2"]:
        raise ValueError(f"Invalid admin method: {method}")

    if gee:
        # Import ee only when needed

        from sepal_ui.scripts.gee_interface import GEEInterface

        su.init_ee()

        # Use provided interface or create a new one
        interface = gee_interface or GEEInterface()

        # Fetch feature collection from GAUL
        feature_collection = pygaul.AdmItems(admin=admin_code)

        # Get properties for naming (async call)
        feature = feature_collection.first()
        properties = await interface.get_info_async(feature.toDictionary(feature.propertyNames()))

        # Build name from ISO code and admin names
        iso_mapping = json.loads(GAUL_ISO_MAPPING.read_text())
        iso = iso_mapping.get(str(properties.get("ADM0_CODE")), "UNK")
        names = [value for prop, value in properties.items() if "NAME" in prop]
        names = [su.normalize_str(n) for n in names]
        names[0] = iso
        name = "_".join(names)

        # For GEE, we don't compute bounds - users can get them from feature_collection if needed
        return AoiResult(
            method=method,
            name=name,
            gdf=None,  # Lazy - users can convert if needed
            feature_collection=feature_collection,
            admin=admin_code,
            gee=True,
        )

    else:
        # Use pygadm for local processing (async)
        gdf = await pygadm.AsyncItems.create(admin=admin_code)

        # Build name from GID and admin names
        r = gdf.iloc[0]
        names = [su.normalize_str(r[c]) for c in gdf.columns if "NAME" in c]
        names[0] = r.GID_0[:3]
        name = "_".join(names)

        return AoiResult(
            method=method,
            name=name,
            gdf=gdf,
            feature_collection=None,
            admin=admin_code,
            gee=False,
        )


def process_draw(
    geo_json: Dict,
    name: str = "",
    gee: bool = True,
    folder: Union[str, Path] = "",
) -> AoiResult:
    """Process a drawn geometry from map interaction.

    Converts a GeoJSON dict (from DrawControl) into an AoiResult.

    Args:
        geo_json: GeoJSON dict with 'features' key from DrawControl.get_data()
        name: Optional name for the AOI. If empty, generates timestamp-based name.
        gee: If True, create Earth Engine FeatureCollection
        folder: Folder for GEE asset export (only used if gee=True)

    Returns:
        AoiResult with the drawn geometry

    Raises:
        ValueError: If geo_json is empty or invalid

    Example:
        ```python
        # From DrawControl
        features = draw_control.get_data()
        result = process_draw(features, name="my_area", gee=False)
        ```
    """
    if not geo_json or not geo_json.get("features"):
        raise ValueError(ms.aoi_sel.exception.no_draw)

    # Clean style properties from features
    cleaned_features = []
    for feat in geo_json["features"]:
        cleaned_feat = feat.copy()
        if "properties" in cleaned_feat and "style" in cleaned_feat.get("properties", {}):
            cleaned_feat["properties"] = {
                k: v for k, v in cleaned_feat["properties"].items() if k != "style"
            }
        cleaned_features.append(cleaned_feat)

    cleaned_geojson = {"type": "FeatureCollection", "features": cleaned_features}

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(cleaned_geojson).set_crs(epsg=4326)

    # Generate name if not provided
    if not name:
        from datetime import datetime as dt

        name = f"drawn_{dt.now().strftime('%Y%m%d_%H%M%S')}"
    else:
        name = su.normalize_str(name)

    feature_collection = None
    if gee:

        su.init_ee()
        feature_collection = su.geojson_to_ee(gdf.__geo_interface__)

    return AoiResult(
        method="DRAW",
        name=name,
        gdf=gdf,
        feature_collection=feature_collection,
        admin=None,
        gee=gee,
    )
