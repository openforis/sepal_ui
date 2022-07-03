import ipyvuetify as v

from sepal_ui import sepalwidgets as sw
from sepal_ui.frontend.styles import map_btn_style


class MapBtn(v.Btn, sw.SepalWidget):
    """
    Btn specifically design to be displayed on a map. It matches all the characteristics of
    the classic leaflet btn but as they are from ipyvuetify we can use them in combination with Menu to produce on-the-map tiles.
    The MapBtn is responsive to theme changes. It only accept icon or 3 letters as children as the space is very limited.
    If both ``logo`` and ``msg`` are filled, msg will have the priority.

    Args:
        logo (str, optional): a fas/mdi fully qualified name.
        name (str, optional): the name of the btn using 3 letters max.
    """

    logo = None
    "(sw.Icon|str): the content of the btn"

    def __init__(self, logo=None, msg=None, **kwargs):

        # create the icon
        if msg is not None:
            self.logo = msg[: min(3, len(msg))].upper()
        elif logo is not None:
            self.logo = sw.Icon(small=True, children=[logo])
        else:
            raise ValueError("at least one of logo or msg need to be set")

        # some parameters are overloaded to match the map requirements
        kwargs["color"] = "text-color"
        kwargs["outlined"] = True
        kwargs["style_"] = " ".join([f"{k}: {v};" for k, v in map_btn_style.items()])
        kwargs["children"] = [self.logo]
        kwargs["icon"] = False

        super().__init__(**kwargs)
