import ipyvuetify as v

from sepal_ui import sepalwidgets as sw
from sepal_ui.frontend.styles import map_btn_style


class MapBtn(v.Btn, sw.SepalWidget):
    """
    Btn specifically design to be displayed on a map. It matches all the characteristics of
    the classic leaflet btn but as they are from ipyvuetify we can use them in combination with Menu to produce on-the-map tiles.
    The MapBtn is responsive to theme changes. It only accept icon or 3 letters as children as the space is very limited.

    Args:
        content (str): a fas/mdi fully qualified name or a string name. If a string name is used, only the 3 first letters will be displayed.
    """

    def __init__(self, content, **kwargs):

        # create the icon
        if content.startswith("mdi") or content.startswith("fas"):
            content = sw.Icon(small=True, children=[content])
        else:
            content = content[: min(3, len(content))].upper()

        # some parameters are overloaded to match the map requirements
        kwargs["color"] = "text-color"
        kwargs["outlined"] = True
        kwargs["style_"] = " ".join([f"{k}: {v};" for k, v in map_btn_style.items()])
        kwargs["children"] = [content]
        kwargs["icon"] = False

        super().__init__(**kwargs)
