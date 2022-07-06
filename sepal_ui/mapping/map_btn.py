import json
import ipyvuetify as v

from sepal_ui import color
from sepal_ui import sepalwidgets as sw
from sepal_ui.frontend import styles as ss


class MapBtn(v.Btn, sw.SepalWidget):
    """
    Btn specifically design to be displayed on a map. It matches all the characteristics of
    the classic leaflet btn but as they are from ipyvuetify we can use them in combination with Menu to produce on-the-map. The MapBtn is responsive to theme changes.
    Tiles. It only accept icon as children as the space is very limited.

    Args:
        logo (str): a fas/mdi fully qualified name
    """

    logo = None
    "(sw.Icon): a sw.Icon"

    def __init__(self, logo, **kwargs):

        # create the icon
        self.logo = sw.Icon(small=True, children=[logo])

        # create the style from default
        style = json.loads((ss.JSON_DIR / "map_btn.json").read_text())
        style.update(background=color.bg)

        # some parameters are overloaded to match the map requirements
        kwargs["color"] = "text-color"
        kwargs["outlined"] = True
        kwargs["style_"] = " ".join([f"{k}: {v};" for k, v in style.items()])
        kwargs["children"] = [self.logo]
        kwargs["icon"] = False

        super().__init__(**kwargs)
