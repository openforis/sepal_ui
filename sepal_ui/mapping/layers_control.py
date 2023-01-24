"""
Extend fonctionalities of the ipyleaflet layer control.
"""
from typing import Optional

from ipyleaflet import Map, TileLayer
from ipywidgets import link

from sepal_ui import sepalwidgets as sw
from sepal_ui.mapping.menu_control import MenuControl


class LayerLine(sw.Html):

    w_checkbox: Optional[sw.SimpleCheckbox] = None
    "the ckecbox to hide/show the layer"

    w_slider: Optional[sw.SimpleSlider] = None
    "the slider linked to the opacity of the layer"

    layer: Optional[TileLayer] = None
    "the layer controlled by the row"

    prev_opacity: float = 1
    "the opacity set before clicking on the checkbox"

    def __init__(self, layer: TileLayer) -> None:
        """
        Html row element to describe a normal layer.

        This Html element include all the controls to manipulate the layer displayed in the map
        - a checkbox to show/hide
        - a slider to change alpha channel

        Args:
            layer: the layer associated to the row
        """
        # save the layer to modify it dynamically
        self.layer = layer

        # create the checkbox, by default layer are visible
        self.w_checkbox = sw.SimpleCheckbox(v_model=True, small=True)
        kwargs = {"style": "width: 10%;", "tag": "td"}
        checkbox_row = sw.Html(children=[self.w_checkbox], **kwargs)

        # create the label
        kwargs = {"style_": "width: 40%;", "tag": "td", "class_": "text-right"}
        label_row = sw.Html(children=[layer.name], **kwargs)

        # create the slider
        self.w_slider = sw.SimpleSlider(v_model=1, max=1, step=0.001, small=True)
        link((layer, "opacity"), (self.w_slider, "v_model"))
        kwargs = {"style_": "width: 50%;", "tag": "td"}
        slider_row = sw.Html(children=[self.w_slider], **kwargs)

        # build a html tr from it
        super().__init__(tag="tr", children=[checkbox_row, label_row, slider_row])


class LayersControl(MenuControl):

    m: Optional[Map] = None
    "the map controlled by the layercontrol"

    def __init__(self, m: Map, **kwargs) -> None:
        """
        Richer layerControl to add some controls over the lyers displayed on the map.

        Each layer is associated to a line where the user can adapt the alpha chanel or even hide it completely

        Args:
            m: the map to display the layers
            kwargs: optional extra parameters for the ipyleaflet.WidgetControl
        """
        # save the map
        self.m = m

        # set the kwargs parameters
        kwargs.setdefault("position", "topright")
        super().__init__(
            icon_content="fa-solid fa-layer-group", card_content="", m=m, **kwargs
        )

        # add js behavior
        self.m.observe(self.update_table, "layers")

    def update_table(self, change: dict) -> None:
        """update the table content."""
        # create a table of layerLine
        rows = [LayerLine(layer) for layer in self.m.layers]
        tbody = sw.Html(tag="tbody", children=rows)
        kwargs = {"class_": "v-no-hover", "dense": True}
        table = sw.SimpleTable(children=[tbody], **kwargs)

        # set the table as children of the widget
        self.menu.children = [table]

        return
