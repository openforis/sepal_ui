"""All modules used to create AOI selection interface.

Package to access all the widget, model and tiles to create an AOI selection interface available in sepal-ui.

Every module content can be called directly from the package.

Example:
    .. jupyter-execute::

        from sepal_ui import aoi

        aoi.AoiTile(gee=False)
"""

from .aoi_model import *
from .aoi_tile import *
from .aoi_view import *
