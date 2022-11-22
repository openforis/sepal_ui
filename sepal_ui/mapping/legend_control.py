import sepal_ui.sepalwidgets as sw
from ipyleaflet import WidgetControl
from ipywidgets import HTML
from sepal_ui.message import ms
from sepal_ui.scripts import utils as su
from traitlets import Bool, Dict, Unicode, observe


class LegendControl(WidgetControl):
    """
    A custom Legend widget ready to be embed in a map

    This Legend can be control though it's different attributes, changin it's position of course but also the orientation ,the keys and their colors.

    .. versionadded:: 2.10.4

    Args:
        legend_dict (dict): the dictionnary to fill the legend values. cannot be empty.
        title (str) title of the legend, if not set a default value in the current language will be used
        vertical (bool): the orientation of the legend. default to True
    """

    title = Unicode(None).tag(sync=True)
    "Unicode: title of the legend."

    legend_dict = Dict(None).tag(sync=True)
    "Dict: dictionary with key as label name and value as color"

    vertical = Bool(None).tag(sync=True)
    "Bool: whether to display the legend in a vertical or horizontal way"

    _html_table = None

    _html_title = None

    def __init__(
        self, legend_dict={}, title=ms.mapping.legend, vertical=True, **kwargs
    ):

        # init traits
        self.title = title
        self.legend_dict = legend_dict
        self.vertical = vertical

        # generate the content based on the init options
        self._html_title = sw.Html(tag="h4", children=[f"{self.title}"])
        self._html_table = sw.Html(tag="table", children=[])

        # create a card inside the widget
        # Be sure that the scroll bar will be shown up when legend horizontal
        self.legend_card = sw.Card(
            attributes={"id": "legend_card"},
            style_="overflow-x:auto; white-space: nowrap;",
            max_width=450,
            max_height=350,
            children=[self._html_title, self._html_table],
        ).hide()

        # set some parameters for the actual widget
        kwargs["widget"] = self.legend_card
        kwargs["position"] = kwargs.pop("position", "bottomright")

        super().__init__(**kwargs)

        self._set_legend(legend_dict)

    def __len__(self):
        """returns the number of elements in the legend"""

        return len(self.legend_dict)

    def hide(self):
        """Hide control by hiding its content"""
        self.legend_card.hide()

    def show(self):
        """Show control by displaying its content"""
        self.legend_card.show()

    @observe("legend_dict", "vertical")
    def _set_legend(self, _):
        """Creates/update a legend based on the class legend_dict member"""

        # Do this to avoid crash when called by trait for the first time
        if self._html_table is None:
            return

        if not self.legend_dict:
            self.hide()
            return

        self.show()

        if self.vertical:
            elements = [
                sw.Html(
                    tag="tr" if self.vertical else "td",
                    children=[
                        sw.Html(tag="td", children=self.color_box(color)),
                        label.capitalize(),
                    ],
                )
                for label, color in self.legend_dict.items()
            ]
        else:
            elements = [
                (
                    sw.Html(
                        tag="td",
                        children=[label.capitalize()],
                    ),
                    sw.Html(
                        tag="td",
                        children=self.color_box(color),
                    ),
                )
                for label, color in self.legend_dict.items()
            ]
            # Flat nested list
            elements = [e for row in elements for e in row]

        self._html_table.children = elements

        return

    @observe("title")
    def _update_title(self, change):
        """Trait method to update the title of the legend"""

        # Do this to avoid crash when called by trait
        if self._html_title is None:
            return

        self._html_title.children = change["new"]

        return

    @staticmethod
    def color_box(color, size=35):
        """Returns an rectangular SVG html element with the provided color"""

        # Define height and width based on the size
        w = size
        h = size / 2

        return [
            HTML(
                f"""
                    <th>
                        <svg width='{w}' height='{h}'>
                        <rect width='{w}' height='{h}' style='fill:{su.to_colors(color)};
                        stroke-width:1;stroke:rgb(255,255,255)'/>
                        </svg>
                    </th>
                """
            )
        ]
