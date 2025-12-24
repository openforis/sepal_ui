"""Solara components for Area of Interest (AOI) selection and management."""

# Core result dataclass
# Admin processing
from .admin import fetch_admin_bounds_async, fetch_admin_items, process_admin
from .aoi_result import AoiResult

# UI components
from .aoi_view import AdminLevelSelector, AoiView, MethodSelect

# Draw processing
from .draw import process_draw

# WMS utilities
from .wms_utils import (
    FAO_GAUL_LAYERS,
    FAO_WMS_BASE_URL,
    WMS_PREVIEW_LAYER_NAME,
    create_wms_preview_layer,
    remove_wms_preview_layer,
)

__all__ = [
    # Core dataclass
    "AoiResult",
    # Admin functions
    "fetch_admin_items",
    "fetch_admin_bounds_async",
    "process_admin",
    # Draw functions
    "process_draw",
    # WMS utilities
    "create_wms_preview_layer",
    "remove_wms_preview_layer",
    "WMS_PREVIEW_LAYER_NAME",
    "FAO_WMS_BASE_URL",
    "FAO_GAUL_LAYERS",
    # UI components
    "AoiView",
    "AdminLevelSelector",
    "MethodSelect",
]
