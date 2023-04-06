"""wrapper for ipyvuetify widgets to unify the display of voila dashboards in the SEPAL plateform.

``sepal_ui`` is a lib designed to create elegant python based dashboard in the SEPAL environment. It is designed on top of the amazing ``ipyvuetify`` library and will help developer to easily create interface for their workflows. By using this libraries, you'll ensure a robust and unified interface for your scripts and a easy and complete integration into the SEPAL dashboard of application.
"""

from sepal_ui.conf import config as config
from sepal_ui.conf import config_file as config_file
from sepal_ui.frontend.styles import SepalColor
from sepal_ui.frontend.styles import get_theme as get_theme

__author__ = """Pierrick Rambaud"""
__email__ = "pierrick.rambaud49@gmail.com"
__version__ = "2.16.2"

color = SepalColor()
'color: the colors of sepal. members are in the following list: "main, darker, bg, primary, accent, secondary, success, info, warning, error, menu". They will render according to the selected theme.'
