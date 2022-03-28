from traitlets import link, Bool, observe
from functools import partial
from datetime import datetime
from pathlib import Path
from itertools import cycle

import ipyvuetify as v
from deprecated.sphinx import versionadded
import pandas as pd
from ipywidgets import jsdlink

import sepal_ui
from sepal_ui.sepalwidgets.sepalwidget import SepalWidget
from sepal_ui import color
from sepal_ui.frontend import js
from sepal_ui.scripts import utils as su
from sepal_ui.message import ms

__all__ = [
    "AppBar",
    "DrawerItem",
    "NavDrawer",
    "Footer",
    "App",
    "LocaleSelect",
    "ThemeSelect",
]


class AppBar(v.AppBar, SepalWidget):
    """
    Custom AppBar widget with the provided title using the sepal color framework

    Args:
        title (str, optional): the title of the app
        translator (sw.Translator, optional): the app translator to pass to the locale selector object
        kwargs(dict, optional): any parameters from a v.AppBar. If set, 'children' and 'app' will be overwritten.
    """

    toogle_button = None
    "v.Btn: The btn to display or hide the drawer to the user"

    title = None
    "v.ToolBarTitle: the widget containing the app title"

    locale = None
    "sw.LocaleSelect: the locale selector of all apps"

    theme = None
    "sw.ThemeSelect: the theme selector of all apps"

    def __init__(self, title="SEPAL module", translator=None, **kwargs):

        self.toggle_button = v.Btn(
            icon=True,
            children=[v.Icon(class_="white--text", children=["fas fa-ellipsis-v"])],
        )

        self.title = v.ToolbarTitle(children=[title])

        self.locale = LocaleSelect(translator=translator)
        self.theme = ThemeSelect()

        # set the default parameters
        kwargs["color"] = kwargs.pop("color", color.main)
        kwargs["class_"] = kwargs.pop("class_", "white--text")
        kwargs["dense"] = kwargs.pop("dense", True)
        kwargs["app"] = True
        kwargs["children"] = [
            self.toggle_button,
            self.title,
            v.Spacer(),
            self.locale,
            self.theme,
        ]

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
        icon(str, optional): the full name of a mdi/fa icon
        card (str, optional): the mount_id of tiles in the app
        href (str, optional): the absolute link to an external web page
        kwargs (optional): any parameter from a v.ListItem. If set, '_metadata', 'target', 'link' and 'children' will be overwritten.
        model (optional): sepalwidget model where is defined the bin_var trait
        bind_var (optional): required when model is selected. Trait to link with 'alert' self trait parameter
    """

    rt = None
    "sw.ResizeTrigger: the trigger to resize maps and other javascript object when jumping from a tile to another"

    alert = Bool(False).tag(sync=True)
    "Bool: trait to control visibility of an alert in the drawer item"

    alert_badge = None
    "v.ListItemAction: red circle to display in the drawer"

    def __init__(
        self,
        title,
        icon=None,
        card=None,
        href=None,
        model=None,
        bind_var=None,
        **kwargs
    ):

        # set the resizetrigger
        self.rt = js.rt

        icon = icon if icon else "far fa-folder"

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

        # cannot be set as a class member because it will be shared with all
        # the other draweritems.
        self.alert_badge = v.ListItemAction(
            children=[v.Icon(children=["fas fa-circle"], x_small=True, color="red")]
        )

        if model:
            if not bind_var:
                raise Exception(
                    "You have selected a model, you need a trait to bind with drawer."
                )

            link((model, bind_var), (self, "alert"))

    @observe("alert")
    def add_notif(self, change):
        """Add a notification alert to drawer"""

        if change["new"]:
            if self.alert_badge not in self.children:
                new_children = self.children[:]
                new_children.append(self.alert_badge)
                self.children = new_children
        else:
            self.remove_notif()

        return

    def remove_notif(self):
        """Remove notification alert"""

        if self.alert_badge in self.children:
            new_children = self.children[:]
            new_children.remove(self.alert_badge)

            self.children = new_children

        return

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

        # Remove notification
        self.remove_notif()

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
            item_code = DrawerItem("Source code", icon="far fa-file-code", href=code)
            code_link.append(item_code)
        if wiki:
            item_wiki = DrawerItem("Wiki", icon="fas fa-book-open", href=wiki)
            code_link.append(item_wiki)
        if issue:
            item_bug = DrawerItem("Bug report", icon="fas fa-bug", href=issue)
            code_link.append(item_bug)

        children = [
            v.List(dense=True, children=self.items),
            v.Divider(),
            v.List(dense=True, children=code_link),
        ]

        # set default parameters
        kwargs["v_model"] = kwargs.pop("v_model", True)
        kwargs["app"] = True
        kwargs["color"] = kwargs.pop("color", color.darker)
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
        kwargs["color"] = kwargs.pop("color", color.main)
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
        navDrawer (sw.NavDrawer, optional): the navdrawer of the application
        translator (sw.Translator, optional): the translator of the app to display language informations
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

    def __init__(
        self,
        tiles=[""],
        appBar=None,
        footer=None,
        navDrawer=None,
        translator=None,
        **kwargs
    ):

        self.tiles = None if tiles == [""] else tiles

        app_children = []

        # create a false appBar if necessary
        if not appBar:
            appBar = AppBar(translator=translator)
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

        # display a warning if the set language cannot be reached
        if translator is not None:
            if translator.match is False:
                msg = ms.locale.fallback.format(translator.targeted, translator.target)
                self.add_banner(msg, type="error")

        # add js event
        self.appBar.locale.observe(self._locale_info, "value")
        self.appBar.theme.observe(self._theme_info, "v_model")

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
    def add_banner(self, msg, id_=None, **kwargs):
        """
        Display an alert object on top of the app to communicate development information to end user (release date, known issues, beta version). The alert is dissmisable and prominent

        Args:
            msg (str): the message to write in the Alert
            kwargs: any arguments of the v.Alert constructor. if set, 'children' will be overwritten.
            id_ (str, optional): unique banner identificator to avoid multiple aggregations.

        Return:
            self
        """

        kwargs["type"] = kwargs.pop("type", "info")
        kwargs["border"] = kwargs.pop("border", "left")
        kwargs["class_"] = kwargs.pop("class_", "mt-5")
        kwargs["transition"] = kwargs.pop("transition", "scroll-x-transition")
        kwargs["prominent"] = kwargs.pop("prominent", True)
        kwargs["dismissible"] = kwargs.pop("dismissible", True)
        kwargs["children"] = [msg]  # cannot be overwritten
        kwargs["attributes"] = {"id": id_}
        kwargs["v_model"] = kwargs.pop("v_model", False)

        # Verify if alert is already in the app.
        children = self.content.children.copy()

        # remove already existing alert
        alert = next((c for c in children if c.attributes.get("id") == id_), False)
        alert is False or children.remove(alert)

        # create alert
        alert = v.Alert(**kwargs)

        # add the alert to the app if not already there
        self.content.children = [alert] + children

        # Display the alert
        alert.v_model = True

        return self

    def _locale_info(self, change):
        """display information about the locale change"""

        if change["new"] != "":
            msg = ms.locale.change.format(change["new"])
            self.add_banner(msg, id_="locale")

        return

    def _theme_info(self, change):
        """display information about the theme change"""

        if change["new"] != "":
            msg = ms.theme.change.format(change["new"])
            self.add_banner(msg, id_="theme")

        return


class LocaleSelect(v.Menu, SepalWidget):
    """
    An language selector for sepal-ui based application.

    It displays the currently requested language (not the one used by the translator).
    When value is changed, the sepal-ui config file is updated. It is designed to be used in a AppBar component.

    .. warning:: as the component is a v.Menu to get the selected value you need to lisen to "value" instead of "v_model".

    .. versionadded:: 2.7.0


    Args:
        translator (sw.Translator, optional): the translator of the app, to match the used language
        kwargs (dict, optional): any arguments for a Btn object, children will be override
    """

    COUNTRIES = pd.read_csv(Path(__file__).parents[1] / "scripts" / "locale.csv")
    "pandas.DataFrame: the country list as a df. columns [code, name, flag]"

    FLAG = "https://flagcdn.com/{}.svg"
    "str: the url of the svg flag images"

    ATTR = {"src": "https://flagcdn.com/gb.svg", "width": "30", "alt": "en-UK"}
    "dict: the default flag parameter, default to english"

    btn = None
    "v.Btn: the btn to click when changing language"

    language_list = None
    "v.List: the list of countries with their flag,name in english, and ISO code"

    def __init__(self, translator=None, **kwargs):

        # extract the available language from the translator
        # default to only en-US if no translator is set
        available_locales = (
            ["en"] if translator is None else translator.available_locales()
        )

        # extract the language information from the translator
        # if not set default to english
        code = "en" if translator is None else translator.target
        loc = self.COUNTRIES[self.COUNTRIES.code == code].squeeze()
        attr = {**self.ATTR, "src": self.FLAG.format(loc.flag), "alt": loc.name}

        kwargs["small"] = kwargs.pop("small", True)
        kwargs["v_model"] = False
        kwargs["v_on"] = "x.on"
        kwargs["children"] = [v.Html(tag="img", attributes=attr, class_="mr-1"), code]
        self.btn = v.Btn(**kwargs)

        self.language_list = v.List(
            dense=True,
            flat=True,
            color=color.menu,
            v_model=True,
            max_height="300px",
            style_="overflow: auto; border-radius: 0 0 0 0;",
            children=[
                v.ListItemGroup(
                    children=self._get_country_items(available_locales), v_model=""
                )
            ],
        )

        super().__init__(
            children=[self.language_list],
            v_model=False,
            close_on_content_click=True,
            v_slots=[{"name": "activator", "variable": "x", "children": self.btn}],
            value=loc.code,
        )

        # add js behaviour
        jsdlink((self.language_list.children[0], "v_model"), (self, "value"))
        self.language_list.children[0].observe(self._on_locale_select, "v_model")

    def _get_country_items(self, locales):
        """get the list of countries as a list of listItem. reduce the list to the available language of the module"""

        country_list = []
        filtered_countries = self.COUNTRIES[self.COUNTRIES.code.isin(locales)]
        for r in filtered_countries.itertuples(index=False):

            attr = {**self.ATTR, "src": self.FLAG.format(r.flag), "alt": r.name}

            children = [
                v.ListItemAction(children=[v.Html(tag="img", attributes=attr)]),
                v.ListItemContent(children=[v.ListItemTitle(children=[r.name])]),
                v.ListItemActionText(children=[r.code]),
            ]

            country_list.append(v.ListItem(value=r.code, children=children))

        return country_list

    def _on_locale_select(self, change):
        """
        adapt the application to the newly selected language

        Display the new flag and country code on the widget btn
        change the value in the config file
        """

        # get the line in the locale dataframe
        loc = self.COUNTRIES[self.COUNTRIES.code == change["new"]].squeeze()

        # change the btn attributes
        attr = {**self.ATTR, "src": self.FLAG.format(loc.flag), "alt": loc.name}
        self.btn.children = [
            v.Html(tag="img", attributes=attr, class_="mr-1"),
            loc.code,
        ]
        self.btn.color = "info"

        # change the paramater file
        su.set_config_locale(loc.code)

        return


class ThemeSelect(v.Btn, SepalWidget):
    """
    A theme selector for sepal-ui based application.

    It displays the currently requested theme (default to dark).
    When value is changed, the sepal-ui config file is updated. It is designed to be used in a AppBar component.

    .. versionadded:: 2.7.0

    Args:
        kwargs (dict, optional): any arguments for a Btn object, children and v_model will be override
    """

    THEME_ICONS = {"dark": "fas fa-moon", "light": "fas fa-sun"}
    "dict: the dictionnry of icons to use for each theme (used as keys)"

    theme = "dark"
    "str: the current theme of the widget (default to dark)"

    def __init__(self, **kwargs):

        # get the current theme name
        self.theme = sepal_ui.get_theme(sepal_ui.config_file)

        # set the btn parameters
        kwargs["x_small"] = kwargs.pop("x_small", True)
        kwargs["fab"] = kwargs.pop("fab", True)
        kwargs["class_"] = kwargs.pop("class_", "ml-2")
        kwargs["children"] = [v.Icon(children=[self.THEME_ICONS[self.theme]])]
        kwargs["v_model"] = self.theme

        # create the btn
        super().__init__(**kwargs)

        # add some js events
        self.on_event("click", self.toggle_theme)

    def toggle_theme(self, widget, event, data):
        """
        toggle the btn icon from dark to light and adapt the configuration file at the same time
        """
        # use a cycle to go through the themes
        theme_cycle = cycle(self.THEME_ICONS.keys())
        next(t for t in theme_cycle if t == self.theme)
        self.theme = next(t for t in theme_cycle)

        # change icon
        self.color = "info"
        self.children[0].children = [self.THEME_ICONS[self.theme]]

        # change the paramater file
        su.set_config_theme(self.theme)

        # trigger other events by changing v_model
        self.v_model = self.theme

        return
