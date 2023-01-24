"""
Extend fonctionalities of the ipyleaflet layer control.
"""
from typing import Optional

from ipyleaflet import Map

from sepal_ui.mapping.menu_control import MenuControl


class LayersControl(MenuControl):

    m: Optional[Map] = None

    def __init__(self, m: Map, **kwargs):
        """
        Richer layerControl to add some controls over the lyers displayed on the map.

        Each layer is associated to a line where the user can adapt the alpha chanel or even hide it completely

        Args:
            m: the map to display the layers
            kwargs: optional extra parameters for the ipyleaflet.WidgetControl
        """
        # set the kwargs parameters
        kwargs.setdefault("position", "topright")
        super().__init__(
            icon_content="fa-solid fa-folder", card_content="", m=m, **kwargs
        )
