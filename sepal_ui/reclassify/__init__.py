"""
All modules used to create an Reclassification interface. 

Package to access all the widget, model and tiles to create an Reclassifying interface. This is compatible with any type of geographic data (vector raster, ee ...).

Every module content can be called directly from the package.

Example:
    ..jupyter-execute::

        from sepal_ui import reclassify
    
        reclassify.ReclassifyTile()
"""

from .parameters import *
from .reclassify_model import *
from .reclassify_tile import *
from .reclassify_view import *
from .table_view import *
