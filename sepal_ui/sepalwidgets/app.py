from functools import partial
from datetime import datetime

import ipyvuetify as v
from deprecated.sphinx import versionadded

from sepal_ui.sepalwidgets.sepalwidget import SepalWidget
from sepal_ui import color
from sepal_ui.frontend.styles import sepal_main, sepal_darker
from sepal_ui.frontend import js

__all__ = ["AppBar", "DrawerItem", "NavDrawer", "Footer", "App"]


class AppBar(v.AppBar, SepalWidget):
    """
    Custom AppBar widget with the provided title using the sepal color framework

    Args:
        title (str, optional): the title of the app
        kwargs(dict, optional): any parameters from a v.AppBar. If set, 'children' and 'app' will be overwritten.
    """

    toogle_button = None
    "v.Btn: The btn to display or hide the drawer to the user"

    title = None
    "v.ToolBarTitle: the widget containing the app title"

    def __init__(self, title="SEPAL module", **kwargs):

        self.toggle_button = v.Btn(
            icon=True,
            children=[v.Icon(class_="white--text", children=["mdi-dots-vertical"])],
        )

        self.title = v.ToolbarTitle(children=[title])

        # set the default parameters
        kwargs["color"] = kwargs.pop("color", sepal_main)
        kwargs["class_"] = kwargs.pop("class_", "white--text")
        kwargs["dense"] = kwargs.pop("dense", True)
        kwargs["app"] = True
        kwargs["children"] = [self.toggle_button, self.title]

        super().__init__(**kwargs)

    def set_title(self, title):
        """
        Set the title of the appBar

        Args:
            title (str): the new app title

        Return:
            self
        """

        self.title.children = [title]

        return self


class DrawerItem(v.ListItem, SepalWidget):
    """
    Custom DrawerItem using the user input.
    If a card is set the drawerItem will trigger the display of all the Tiles in the app that have the same mount_id.
    If an href is set, the drawer will open the link in a new tab

    Args:
        title (str): the title of the drawer item
        icon(str, optional): the full name of a mdi-icon
        card (str, optional): the mount_id of tiles in the app
        href (str, optional): the absolute link to an external web page
        kwargs (optional): any parameter from a v.ListItem. If set, '_metadata', 'target', 'link' and 'children' will be overwritten.
    """

    rt = None
    "sw.ResizeTrigger: the trigger to resize maps and other javascript object when jumping from a tile to another"

    def __init__(self, title, icon=None, card=None, href=None, **kwargs):

        # set the resizetrigger
        self.rt = js.rt

        icon = icon if icon else "mdi-folder-outline"

        children = [
            v.ListItemAction(children=[v.Icon(class_="white--text", children=[icon])]),
            v.ListItemContent(
                children=[v.ListItemTitle(class_="white--text", children=[title])]
            ),
        ]

        # set default parameters
        kwargs["link"] = True
        kwargs["children"] = children
        kwargs["input_value"] = kwargs.pop("input_value", False)
        if href:
            kwargs["href"] = href  # cannot be set twice anyway
            kwargs["target"] = "_blank"
            kwargs["_metadata"] = kwargs.pop("_metadata", None)
        elif card:
            kwargs["_metadata"] = {"card_id": card}
            kwargs["href"] = kwargs.pop("href", None)
            kwargs["target"] = kwargs.pop("target", None)

        # call the constructor
        super().__init__(**kwargs)

    def display_tile(self, tiles):
        """
        Display the apropriate tiles when the item is clicked.
        The tile to display will be all tile in the list with the mount_id as the current object

        Args:
            tiles ([sw.Tile]) : the list of all the available tiles in the app

        Return:
            self
        """

        self.on_event("click", partial(self._on_click, tiles=tiles))

        return self

    def _on_click(self, widget, event, data, tiles):

        for tile in tiles:
            if self._metadata["card_id"] == tile._metadata["mount_id"]:
                tile.show()
            else:
                tile.hide()

        # trigger the resize event
        self.rt.resize()

        # change the current item status
        self.input_value = True

        return self


class NavDrawer(v.NavigationDrawer, SepalWidget):
    """
    Custom NavDrawer using the different DrawerItems of the user and the sepal color framework.
    The drawer can include links to the github page of the project for wiki, bugs and repository.

    Args:
        item ([sw.DrawerItem]): the list of all the drawerItem to display in the drawer. This items should pilote the different tile visibility
        code (str, optional): the absolute link to the source code
        wiki (str, optional): the absolute link the the wiki page
        issue (str, optional): the absolute link to the issue tracker
        kwargs (optional) any parameter from a v.NavigationDrawer. If set, 'app' and 'children' will be overwritten.
    """

    items = []
    "list: the list of all the drawerItem to display in the drawer"

    def __init__(self, items=[], code=None, wiki=None, issue=None, **kwargs):

        self.items = items

        code_link = []
        if code:
            item_code = DrawerItem("Source code", icon="mdi-file-code", href=code)
            code_link.append(item_code)
        if wiki:
            item_wiki = DrawerItem("Wiki", icon="mdi-book-open-page-variant", href=wiki)
            code_link.append(item_wiki)
        if issue:
            item_bug = DrawerItem("Bug report", icon="mdi-bug", href=issue)
            code_link.append(item_bug)

        children = [
            v.List(dense=True, children=self.items),
            v.Divider(),
            v.List(dense=True, children=code_link),
        ]

        # set default parameters
        kwargs["v_model"] = kwargs.pop("v_model", True)
        kwargs["app"] = True
        kwargs["color"] = kwargs.pop("color", sepal_darker)
        kwargs["children"] = children

        # call the constructor
        super().__init__(**kwargs)

        # bind the javascripts behavior
        for i in self.items:
            i.observe(self._on_item_click, "input_value")

    def display_drawer(self, toggleButton):
        """
        Bind the drawer to the app toggleButton

        Args:
            toggleButton(v.Btn) : the button that activate the drawer
        """

        toggleButton.on_event("click", self._on_drawer_click)

        return self

    def _on_drawer_click(self, widget, event, data):
        """
        Toggle the drawer visibility
        """

        self.v_model = not self.v_model

        return self

    def _on_item_click(self, change):
        """
        Deactivate all the other items when on of the is activated
        """
        if change["new"] is False:
            return self

        # reset all others states
        for i in self.items:
            if i != change["owner"]:
                i.input_value = False

        return self


class Footer(v.Footer, SepalWidget):
    """
    Custom Footer with cuzomizable text.
    Not yet capable of displaying logos

    Args:
        text (str, optional): the text to display in the future
        kwargs (optional): any parameter from a v.Footer. If set ['app', 'children'] will be overwritten.
    """

    def __init__(self, text="", **kwargs):

        text = text if text != "" else "SEPAL \u00A9 {}".format(datetime.today().year)

        # set default parameters
        kwargs["color"] = kwargs.pop("color", sepal_main)
        kwargs["class_"] = kwargs.pop("class_", "white--text")
        kwargs["app"] = True
        kwargs["children"] = [text]

        # call the constructor
        super().__init__(**kwargs)


class App(v.App, SepalWidget):
    """
    Custom App display with the tiles created by the user using the sepal color framework.
    Display false appBar if not filled. Navdrawer is fully optionnal.
    The drawerItem will be linked to the app tile and they will be able to control their display
    If the navdrawer exist, it will be linked to the appbar togglebtn

    Args:
        tiles ([sw.Tile]): the tiles of the app
        appBar (sw.AppBar, optional): the appBar of the application
        footer (sw.Footer, optional): the footer of the application
        navDrawer (sw.NavDrawer): the navdrawer of the application
        kwargs (optional) any parameter from a v.App. If set, 'children' will be overwritten.
    """

    tiles = []
    "list: the tiles of the app"

    appBar = None
    "sw.AppBar: the AppBar of the application"

    footer = None
    "sw.Footer: the footer of the application"

    navDrawer = None
    "sw.NavDrawer: the navdrawer of the application"

    content = None
    "v.Content: the tiles organized in a fluid container"

    def __init__(self, tiles=[""], appBar=None, footer=None, navDrawer=None, **kwargs):

        self.tiles = None if tiles == [""] else tiles

        app_children = []

        # create a false appBar if necessary
        if not appBar:
            appBar = AppBar()
        self.appBar = appBar
        app_children.append(self.appBar)

        # add the navDrawer if existing
        self.navDrawer = None
        if navDrawer:
            # bind app tile list to the navdrawer
            for di in navDrawer.items:
                di.display_tile(tiles)

            # link it with the appbar
            navDrawer.display_drawer(self.appBar.toggle_button)

            # add the drawers to the children
            self.navDrawer = navDrawer
            app_children.append(self.navDrawer)

        # add the content of the app
        self.content = v.Content(children=[v.Container(fluid=True, children=tiles)])
        app_children.append(self.content)

        # add the footer if existing
        if footer:
            self.footer = footer
            app_children.append(self.footer)

        # create a negative overlay to force the background color
        bg = v.Overlay(color=color.bg, opacity=1, style_="transition:unset", z_index=-1)

        # set default parameters
        kwargs["v_model"] = kwargs.pop("v_model", None)
        kwargs["children"] = [bg, *app_children]

        # call the constructor
        super().__init__(**kwargs)

    def show_tile(self, name):
        """
        Select the tile to display when the app is launched

        Args:
            name (str): the mount-id of the tile(s) to display

        Return:
            self
        """
        # show the tile
        for tile in self.tiles:
            if name == tile._metadata["mount_id"]:
                tile.show()
            else:
                tile.hide()

        # activate the drawerItem
        if self.navDrawer:
            items = (i for i in self.navDrawer.items if i._metadata is not None)
            for i in items:
                if name == i._metadata["card_id"]:
                    i.input_value = True

        return self

    @versionadded(version="2.4.1", reason="New end user interaction method")
    def add_banner(self, msg, **kwargs):
        """
        Display an alert object on top of the app to communicate development information to end user (release date, known issues, beta version). The alert is dissmisable and prominent

        Args:
            msg (str): the message to write in the Alert
            kwargs: any arguments of the v.Alert constructor. if set, 'children' will be overwritten.

        Return:
            self
        """

        kwargs["type"] = kwargs.pop("type", "info")
        kwargs["border"] = kwargs.pop("border", "left")
        kwargs["class_"] = kwargs.pop("class_", "mt-5")
        kwargs["transition"] = kwargs.pop("transition", "slide-x-transition")
        kwargs["prominent"] = kwargs.pop("prominent", True)
        kwargs["dismissible"] = kwargs.pop("dismissible", True)
        kwargs["children"] = [msg]  # cannot be overwritten

        # create the alert
        alert = v.Alert(**kwargs)

        # add the alert to the app
        self.content.children = [alert] + self.content.children.copy()

        return self
