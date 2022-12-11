from pathlib import Path

import ipyvuetify as v
from ipyleaflet import WidgetControl
from IPython.display import Javascript, display

from sepal_ui.mapping.map_btn import MapBtn


class FullScreenControl(WidgetControl):
    """
    A custom Fullscreen Button ready to be embed in a map object.

    This button will force the display of the map in fullscreen mode. It should be used instead of the built-in ipyleaflet FullscreenControl if your map is embeding ipyvuetify widgets. I tends to solve the issue raised here: https://github.com/widgetti/ipyvuetify/issues/141. The idea is to fake the fullscreen display by forcing the map container to extend to the full extend of the screen without using a z-index superior to the ipyvuetify overlay.
    simply click on it and the map will automatically expand

    .. versionadded:: 2.7.0

    Args:
        m (SepalMap): the map on which the mutated CSS will be applied (Only work with SepalMap as we are querying the _id)
        fullscreen (bool, optional): either the map should be displayed in fullscreen by default. default to false.
        fullapp (bool, optional): either or not the map will be used as the sole widget/tile of an application
        kwargs (optional): any available arguments from a ipyleaflet WidgetControl
    """

    ICONS = ["fa-solid fa-expand", "fa-solid fa-compress"]
    "list: The icons that will be used to toggle between expand and compressed mode"

    METHODS = ["embed", "fullscreen"]
    "list: The javascript methods name to be used to switch from expand to compress mode"

    zoomed = None
    "bool: the current zoomed level: ``True`` for expanded and ``False`` for compressed"

    w_btn = None
    "ipywidget.Button: the btn to display on the map"

    template = None
    "ipyvuetify.VuetifyTemplate: embeds the 2 javascripts methods to change the rendering of the map"

    def __init__(self, m, fullscreen=False, fullapp=False, **kwargs):

        # set the offset
        offset = "48px" if fullapp else "0px"

        # register the required zoom value
        self.zoomed = fullscreen

        # create a btn
        self.w_btn = MapBtn(self.ICONS[self.zoomed])

        # overwrite the widget set in the kwargs (if any)
        kwargs["widget"] = self.w_btn
        kwargs["position"] = kwargs.pop("position", "topleft")
        kwargs["transparent_bg"] = True

        # create the widget
        super().__init__(**kwargs)

        # add javascrip behaviour
        self.w_btn.on_event("click", self.toggle_fullscreen)

        # save the 2 fullscrenn js code in a table 0 for embeded and 1 for fullscreen
        js_dir = Path(__file__).parents[1] / "frontend/js"
        embed = (js_dir / "jupyter_embed.js").read_text() % m._id
        full = (js_dir / "jupyter_fullscreen.js").read_text() % (m._id, offset)

        # template with js behaviour
        # "jupyter_fullscreen" place tje "leaflet-container element on the front screen
        # and expand it's display to the full screen
        # "jupyter_embed" reset all the changed parameter
        # both trigger the resize event to force the reload of the Tilelayers
        self.template = v.VuetifyTemplate(
            template=(
                "<script>{methods: {jupyter_embed(){%s}, jupyter_fullscreen(){%s}}}</script>"
                % (embed, full)
            )
        )
        display(self.template)

        # display the map in the requested default state
        js = full if self.zoomed else embed
        display(Javascript(js))

    def toggle_fullscreen(self, widget, event, data):
        """
        Toggle the fullscreen state of the map by sending the required javascript method,
        changing the w_btn icons and the zoomed state of the control.
        """

        # change the zoom state
        self.zoomed = not self.zoomed

        # change button icon
        self.w_btn.children[0].children = [self.ICONS[self.zoomed]]

        # zoom
        self.template.send({"method": self.METHODS[self.zoomed], "args": []})

        return
