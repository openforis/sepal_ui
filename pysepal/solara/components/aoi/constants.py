"""Constants for FAO GAUL data services.

Centralized configuration for FAO GAUL WMS/WFS service URLs and layer names.
"""

# FAO GAUL WMS Configuration
FAO_WMS_BASE_URL = "https://data.apps.fao.org/map/gsrv/gsrv1/gaul/wms"

# FAO GAUL WFS Configuration
FAO_WFS_BASE_URL = "https://data.apps.fao.org/map/gsrv/gsrv1/gaul/wfs"

# FAO GAUL layers (used by both WMS and WFS)
FAO_GAUL_LAYERS = {
    0: "gaul:gaul_2024_l0",
    1: "gaul:g2024_2023_1",
    2: "gaul:g2024_2023_2",
}

# WMS preview layer name constant
WMS_PREVIEW_LAYER_NAME = "aoi_wms_preview"
