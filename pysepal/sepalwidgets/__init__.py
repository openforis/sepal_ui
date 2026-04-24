"""All the widgets available in pysepal.

Package to access all the widgets available in pysepal. The widgets are all derived from ``IpyvuetifyWidget`` and ``SepalWidget``. They can be used to build interfaces in applications. ``pysepal.sepalwidgets`` includes all the widgets from ``ipyvuetify`` and some extra ones that are useful to build GIS related applications.

Everything module content can be called directly from the package.

Example:
    .. jupyter-execute::

        from pysepal import sepalwidgets as sw

        sw.Btn()
"""

from pysepal.sepalwidgets.sepal_ipyvuetify import *  # noqa: I

# import and/or overwrite with our customized widgets
from pysepal.sepalwidgets.sepalwidget import *
from pysepal.sepalwidgets.alert import *
from pysepal.sepalwidgets.app import *
from pysepal.sepalwidgets.btn import *
from pysepal.sepalwidgets.inputs import *
from pysepal.sepalwidgets.tile import *
from pysepal.sepalwidgets.widget import *
from pysepal.sepalwidgets.radio import *
