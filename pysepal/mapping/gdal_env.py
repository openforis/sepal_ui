"""Sanitize GDAL/PROJ data environment variables.

SEPAL's system GDAL exports GDAL_DATA, PROJ_LIB and PROJ_DATA into every module
venv, pointing at data files for a different GDAL build than the venv's wheels.
That breaks raster reads, so drop them before anything imports rasterio.

Paths inside the interpreter's own prefix are kept: they are this environment's
own GDAL stack, and pyogrio and osgeo break without them. This cannot fix a mixed
conda/wheel install, where a wheel's own libgdal lives in that prefix too.
"""

import os
import sys
from pathlib import Path

GDAL_ENV_VARS = ("GDAL_DATA", "PROJ_LIB", "PROJ_DATA")
"""Data-directory variables to sanitize.

``PROJ_LIB`` is PROJ's pre-9.1 name for ``PROJ_DATA``; both are still exported in
the wild, so a foreign PROJ install can arrive through either one.
"""


def _is_own_path(path: str) -> bool:
    """Whether ``path`` resolves under one of this interpreter's own prefixes.

    ``sys.base_prefix`` differs from ``sys.prefix`` inside a venv, and a venv
    layered on a conda env inherits that env's GDAL stack, so both count as ours.
    """
    if not path:
        return False

    try:
        resolved = Path(path).resolve()
        prefixes = [Path(prefix).resolve() for prefix in (sys.prefix, sys.base_prefix)]
    except OSError:
        return False

    return any(resolved.is_relative_to(prefix) for prefix in prefixes)


def prune_foreign_gdal_env() -> None:
    """Delete the GDAL/PROJ data variables that point outside this environment."""
    for var in GDAL_ENV_VARS:
        path = os.environ.get(var)
        if path is not None and not _is_own_path(path):
            del os.environ[var]
