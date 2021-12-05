from pathlib import Path

import ipyvuetify as v

from sepal_ui.sepalwidgets.sepalwidget import SepalWidget
from sepal_ui.sepalwidgets.widget import Markdown
from sepal_ui.scripts import utils as su

__all__ = ["Tile", "TileAbout", "TileDisclaimer"]


class Tile(v.Layout, SepalWidget):
    """
    Custom Layout widget for the sepal UI framework.
    It an helper to build a consistent tiling system.
    Tile objects are indeed compatible with the other classes from sepal_ui.

    Args:
        id_ (str): the tile id that will be written in its mount_id _metadata attribute
        title (str): the title of the Tile
        inputs ([list]): the list of widget to display inside the tile
        btn (v.Btn): the process btn
        alert (sw.Alert): the alert to display process informations to the end user
        kwargs (optional): any parameter from a v.Layout. if set, 'children' and '_metadata' will be overwritten.
    """

    btn = None
    "v.btn: the process btn"

    alert = None
    "sw.Alert: the alert to display process informations to the end user"

    title = None
    "v.Html: the title of the Tile"

    def __init__(self, id_, title, inputs=[""], btn=None, alert=None, **kwargs):

        self.btn = btn
        if btn:
            inputs.append(btn)

        self.alert = alert
        if alert:
            inputs.append(alert)

        self.title = v.Html(xs12=True, tag="h2", children=[title])

        content = [v.Flex(xs12=True, children=[widget]) for widget in inputs]

        card = v.Card(
            class_="pa-5", raised=True, xs12=True, children=[self.title] + content
        )

        # set some default parameters
        kwargs["_metadata"] = {"mount_id": id_}
        kwargs["row"] = kwargs.pop("row", True)
        kwargs["align_center"] = kwargs.pop("align_center", True)
        kwargs["class_"] = kwargs.pop("class_", "ma-5 d-inline")
        kwargs["children"] = [card]

        # call the constructor
        super().__init__(**kwargs)

    def nest(self):
        """
        Prepare the tile to be used as a nested component in a tile.
        the elevation will be set to 0 and the title remove from children.
        The mount_id will also be changed to nested

        Return:
            self
        """

        # remove id
        self._metadata["mount_id"] = "nested_tile"

        # remove elevation
        self.elevation = False

        # remove title
        self.set_title()

        return self

    def set_content(self, inputs):
        """
        Replace the current content of the tile with the provided inputs. it will keep the output and btn widget if existing.

        Args:
            inputs ([list]): the list of widget to display inside the tile

        Return:
            self
        """

        # create the widgets
        content = [v.Flex(xs12=True, children=[widget]) for widget in inputs]

        # add the output (if existing)
        if self.title:
            content = [self.title] + content

        if self.alert:
            content = content + [self.alert]

        if self.btn:
            content = content + [self.btn]

        self.children[0].children = content

        return self

    def set_title(self, title=None):
        """
        Replace the current title and activate it.
        If no title is provided, the title is removed from the tile content

        Args:
            title (str, optional): the new title of the object

        Return:
            self
        """

        # set the title text
        self.title.children = [str(title)]

        # add the title if it's deactivated
        if title and self.title not in self.children[0].children:
            self.children[0].children = [self.title] + self.children[0].children.copy()

        # remove it if it's deactivated
        elif self.title in self.children[0].children and not title:
            self.children[0].children = self.children[0].children.copy()[
                1:
            ]  # it's the first one

        return self

    def get_title(self):
        """
        Return the current title of the tile

        Return:
            (str): the title
        """

        return self.title.children[0]

    def toggle_inputs(self, fields_2_show, fields):
        """
        Display only the widgets that are part of the input_list. the widget_list is the list of all the widgets of the tile.

        Args:
            fields_2_show ([v.widget]) : the list of input to be display
            fields ([v.widget]) : the list of the tile widget

        Return:
            self
        """

        for field in fields:
            if field in fields_2_show:
                su.show_component(field)
            else:
                su.hide_component(field)

        return self

    def get_id(self):
        """
        Return the mount_id value

        Return:
            (str): the moun_id value from _metadata dict
        """

        return self._metadata["mount_id"]


class TileAbout(Tile):
    """
    Create an about tile using a .md file.
    This tile will have the "about_widget" id and "About" title.

    Args:
        pathname (str | pathlib.Path): the path to the .md file
    """

    def __init__(self, pathname, **kwargs):

        if type(pathname) == str:
            pathname = Path(pathname)

        # read the content and transform it into a html
        with pathname.open() as f:
            about = f.read()

        content = Markdown(about)

        super().__init__("about_tile", "About", inputs=[content])


class TileDisclaimer(Tile):
    """
    Create a about tile using a the generic disclaimer .md file.
    This tile will have the "about_widget" id and "Disclaimer" title.
    """

    def __init__(self):

        pathname = Path(__file__).parents[1] / "scripts" / "disclaimer.md"

        # read the content and transform it into a html
        with pathname.open() as f:
            disclaimer = f.read()

        content = Markdown(disclaimer)

        super().__init__("about_tile", "Disclaimer", inputs=[content])
