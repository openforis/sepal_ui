"""
Extend fonctionalities of the ipyleaflet layer control.
"""
from typing import Optional

from ipyleaflet import Map, TileLayer
from ipywidgets import link

from sepal_ui import sepalwidgets as sw
from sepal_ui.mapping.menu_control import MenuControl


class BaseLine(sw.Html):

    w_radio: Optional[sw.SimpleCheckbox] = None
    "the radio to hide/show the layer"

    def __init__(self, layer: TileLayer) -> None:
        """
        Html row element to describe a base layer.

        This Html element include all the controls to manipulate the basemap displayed in the map
        - a checkbox to show/hide (it will behave like a radio)

        Args:
            layer: the layer associated to the row
        """
        # create the checkbox, by default layer are visible
        self.w_radio = sw.Radio(small=True, value=layer.name)
        kwargs = {"style": "width: 10%;", "tag": "td"}
        radio_row = sw.Html(children=[self.w_radio], **kwargs)

        # create the label
        kwargs = {"style_": "width: 40%;", "tag": "td", "class_": "text-right"}
        label_row = sw.Html(children=[layer.name], **kwargs)

        # create an empty row to align on
        kwargs = {"style_": "width: 50%;", "tag": "td"}
        empty_row = sw.Html(children=[""], **kwargs)

        # build a html tr from it
        super().__init__(tag="tr", children=[radio_row, label_row, empty_row])

        # add js behavior
        link((layer, "visible"), (self.w_radio, "active"))


class LayerLine(sw.Html):

    w_checkbox: Optional[sw.SimpleCheckbox] = None
    "the ckeckbox to hide/show the layer"

    w_slider: Optional[sw.SimpleSlider] = None
    "the slider linked to the opacity of the layer"

    def __init__(self, layer: TileLayer) -> None:
        """
        Html row element to describe a normal layer.

        This Html element include all the controls to manipulate the layer displayed in the map
        - a checkbox to show/hide
        - a slider to change alpha channel

        Args:
            layer: the layer associated to the row
        """
        # create the checkbox, by default layer are visible
        self.w_checkbox = sw.SimpleCheckbox(v_model=True, small=True, label=layer.name)
        kwargs = {"style": "width: 50%;", "tag": "td"}
        checkbox_row = sw.Html(children=[self.w_checkbox], **kwargs)

        # create the label
        kwargs = {"style_": "width: 40%;", "tag": "td", "class_": "text-right"}
        label_row = sw.Html(children=[layer.name], **kwargs)

        # create the slider
        self.w_slider = sw.SimpleSlider(v_model=1, max=1, step=0.001, small=True)
        kwargs = {"style_": "width: 50%;", "tag": "td"}
        slider_row = sw.Html(children=[self.w_slider], **kwargs)

        # build a html tr from it
        super().__init__(tag="tr", children=[checkbox_row, label_row, slider_row])

        # add js behavior
        link((layer, "opacity"), (self.w_slider, "v_model"))
        link((self.w_checkbox, "v_model"), (layer, "visible"))
        self.w_checkbox.observe(self._toggle_slider, "v_model")

    def _toggle_slider(self, *args) -> None:
        """Toggle the modification of the slider."""
        self.w_slider.disabled = not self.w_checkbox.v_model

        return


class LayersControl(MenuControl):

    m: Optional[Map] = None
    "the map controlled by the layercontrol"

    fake_group: Optional[sw.RadioGroup] = None
    "As radio button cannot behave individually we add an extra GroupRadio that will nor be displayed"

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
        """
        Update the table content.
        """
        # create a table of layerLine
        rows = [LayerLine(lyr) for lyr in self.m.layers if lyr.base is False]
        tbody = sw.Html(tag="tbody", children=rows)
        kwargs = {"class_": "v-no-hover", "dense": True}
        layer_table = sw.SimpleTable(children=[tbody], **kwargs)

        # create another table of basemapLine
        bases = [lyr for lyr in self.m.layers if lyr.base is True]
        rows = [BaseLine(lyr) for lyr in bases]
        current = next(lyr for lyr in bases if lyr.visible is True)
        tbody = sw.Html(tag="tbody", children=rows)
        kwargs = {"class_": "v-no-hover", "dense": True}
        base_table = sw.SimpleTable(children=[tbody], **kwargs)
        base_group = sw.RadioGroup(v_model=current.name, children=[base_table])

        # set the table as children of the widget
        self.menu.children = [base_group, sw.Divider(), layer_table]

        return
