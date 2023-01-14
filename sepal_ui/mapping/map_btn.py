"""
Based ``SepalMap`` Btn.
"""

import json

import ipyvuetify as v

from sepal_ui import color
from sepal_ui import sepalwidgets as sw
from sepal_ui.frontend import styles as ss


class MapBtn(v.Btn, sw.SepalWidget):
    def __init__(self, content: str, **kwargs) -> None:
        """
        Btn specifically design to be displayed on a map.

        It matches all the characteristics of
        the classic leaflet btn but as they are from ipyvuetify we can use them in combination with Menu to produce on-the-map tiles.
        The MapBtn is responsive to theme changes. It only accept icon or 3 letters as children as the space is very limited.

        Args:
            content: a fa-solid/mdi fully qualified name or a string name. If a string name is used, only the 3 first letters will be displayed.
        """
        # create the icon
        if content.startswith("mdi-") or content.startswith("fa-solid fa-"):
            content = sw.Icon(small=True, children=[content])
        else:
            content = content[: min(3, len(content))].upper()

        # create the style from default
        style = json.loads((ss.JSON_DIR / "map_btn.json").read_text())
        style.update(background=color.bg)

        # some parameters are overloaded to match the map requirements
        kwargs["color"] = "text-color"
        kwargs["outlined"] = True
        kwargs["style_"] = " ".join([f"{k}: {v};" for k, v in style.items()])
        kwargs["children"] = [content]
        kwargs["icon"] = False

        super().__init__(**kwargs)
