"""Sanitize GDAL/PROJ data environment variables."""

import os
import sys


def prune_foreign_gdal_env() -> None:
    """Remove GDAL/PROJ data paths that belong to a foreign GDAL install.

    On SEPAL the system GDAL exports ``GDAL_DATA``/``PROJ_LIB`` pointing at
    data files for a different GDAL version than the one bundled with the
    rasterio wheel, which breaks raster reads. Paths inside ``sys.prefix``
    belong to this environment's own GDAL stack (e.g. conda) and are kept:
    removing them breaks GDAL data discovery for the environment's own
    GDAL-based libraries (pyogrio, osgeo).
    """
    for var in ("GDAL_DATA", "PROJ_LIB"):
        path = os.environ.get(var)
        if path is not None and not path.startswith(sys.prefix):
            del os.environ[var]
