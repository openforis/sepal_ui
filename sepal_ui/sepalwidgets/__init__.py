# overwrite all the ipyvuetify widgets
from sepal_ui.sepalwidgets.sepalwidget import SepalWidget, TYPES
import ipyvuetify as v


# overwrite html
class Html(v.Html, SepalWidget):
    pass


# overwrite classes
_c_list = [
    c for c in dir(v.generated) if not c.startswith("__") and c != "VuetifyWidget"
]

for c in _c_list:

    class _tmp(getattr(v, c), SepalWidget):
        pass

    locals()[c] = _tmp
del _tmp

# import and/or overwrite with our customized widgets
from sepal_ui.sepalwidgets.widget import *
from sepal_ui.sepalwidgets.alert import *
from sepal_ui.sepalwidgets.btn import *
from sepal_ui.sepalwidgets.app import *
from sepal_ui.sepalwidgets.tile import *
from sepal_ui.sepalwidgets.inputs import *
