"""All the widgets available in sepal-ui.

Package to access all the widget available in sepal-ui. The widgets are all derived from ``IpyvuetifyWidget`` and ``SepalWidget``. They can be used to build interfaces in applications. ``sepal_ui.sepalwidgets`` include all the widgets from `ìpyvuetify`` and some extra one that are usefull to build GIS related applications.

Everything module content can be called directly from the package.

Example:
    .. jupyter-execute::

        from sepal_ui import sepalwidgets as sw

        sw.Btn()
"""

from sepal_ui.sepalwidgets.sepal_ipyvuetify import *  # noqa: I

# import and/or overwrite with our customized widgets
from sepal_ui.sepalwidgets.sepalwidget import *
from sepal_ui.sepalwidgets.alert import *
from sepal_ui.sepalwidgets.app import *
from sepal_ui.sepalwidgets.btn import *
from sepal_ui.sepalwidgets.inputs import *
from sepal_ui.sepalwidgets.tile import *
from sepal_ui.sepalwidgets.widget import *
from sepal_ui.sepalwidgets.radio import *
