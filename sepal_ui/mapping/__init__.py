"""All modules used to create a application ``Map``.

The ``SepalMap`` is inheriting from the **ipyleaflet** ``Map``. It has been customized to support additional widgets as controls based on **ipyvuetify**. It is also fully compatible with the **sepal-ui** framework thanks to frontend modifications.

The main object is the ``SepalMap``that should be used in favor of ``Map`` in **sepal-ui** framework. The others are predisgned controls that can be helpful to speed up developments.
``SepalMap`` is fully compatible with Google Earth Engine layers.

Every module content can be called directly from the package.

Example:
    .. jupyter-execute::

        from sepal_ui import mapping as sm

        sm.SepalMap(gee=False)
"""

from .aoi_control import *
from .draw_control import *
from .fullscreen_control import *
from .inspector_control import *
from .layer import *
from .layer_state_control import *
from .layers_control import *
from .legend_control import *
from .map_btn import *
from .marker_cluster import *
from .menu_control import *
from .sepal_map import *
from .zoom_control import *
