from ipywidgets import HTML
from traitlets import Bool, Dict, Unicode, observe

import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import utils as su


class Legend(sw.Card):
    """
    Custom Card to display and update map legend

    """

    title = Unicode("Legend").tag(sync=True)
    "str: title of the legend. defaults to 'Legend'"

    legend_dict = Dict({}).tag(sync=True)
    "dict: dictionary with key as label name and value as color"

    vertical = Bool(True).tag(sync=True)
    "bool: whether to display the legend in a vertical or horizontal way"

    _html_table = None

    def __init__(self, legend_dict, title="Legend", vertical=True, **kwargs):

        self.style_ = "overflow-x:auto; white-space: nowrap;"
        self.max_width = 450
        self.max_height = 350
        self.title = title
        self.legend_dict = legend_dict
        self.vertical = vertical

        self.html_title = sw.Html(tag="h4", children=[f"{self.title}"])
        self._html_table = sw.Html(tag="table", children=[])
        self.children = [self.html_title, self._html_table]

        super().__init__(**kwargs)

        self.set_legend(None)

    @observe("legend_dict", "vertical")
    def set_legend(self, _):
        """Creates/update a legend based on the class legend_dict parameter"""

        # Do this to avoid crash when called by trait
        if not self._html_table:
            return

        if self.vertical:
            elements = [
                sw.Html(
                    tag="tr" if self.vertical else "td",
                    children=[sw.Html(tag="td", children=self.color_box(color)), label],
                )
                for label, color in self.legend_dict.items()
            ]
        else:
            elements = [
                (
                    sw.Html(
                        tag="td",
                        children=[label],
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

    @observe("title")
    def _update_title(self, change):
        """Trait method to update the title of the legend"""
        self.html_title.children = change["new"]

    @staticmethod
    def color_box(color, size=30):
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
