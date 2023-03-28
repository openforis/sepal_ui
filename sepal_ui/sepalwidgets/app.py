"""Custom widgets relative to user application framework.

Gather the customized ``ipyvuetifyWidgets`` used to create the application framework.
All the content of this modules is included in the parent ``sepal_ui.sepalwidgets`` package. So it can be imported directly from there.

Example:
    .. jupyter-execute::

        from sepal_ui import sepalwidgets as sw

        sw.LocaleSelect()
"""

from datetime import datetime
from itertools import cycle
from pathlib import Path
from typing import Dict, List, Optional, Union

import ipyvuetify as v
import pandas as pd
import traitlets as t
from deprecated.sphinx import versionadded, versionchanged
from ipywidgets import jsdlink
from traitlets import link, observe
from typing_extensions import Self

from sepal_ui import color
from sepal_ui.frontend.resize_trigger import ResizeTrigger, rt
from sepal_ui.frontend.styles import get_theme
from sepal_ui.message import ms
from sepal_ui.model import Model
from sepal_ui.scripts import utils as su
from sepal_ui.sepalwidgets.alert import Banner
from sepal_ui.sepalwidgets.sepalwidget import SepalWidget
from sepal_ui.translator import Translator

__all__ = [
    "AppBar",
    "DrawerItem",
    "NavDrawer",
    "Footer",
    "App",
    "LocaleSelect",
    "ThemeSelect",
]


class LocaleSelect(v.Menu, SepalWidget):

    COUNTRIES: pd.DataFrame = pd.read_parquet(
        Path(__file__).parents[1] / "data" / "locale.parquet"
    )
    "the country list as a df. columns [code, name, flag]"

    FLAG: str = "https://flagcdn.com/{}.svg"
    "the url of the svg flag images"

    ATTR: Dict[str, str] = {
        "src": "https://flagcdn.com/gb.svg",
        "width": "30",
        "alt": "en-UK",
    }
    "the default flag parameter, default to english"

    btn: Optional[v.Btn] = None
    "the btn to click when changing language"

    language_list: Optional[v.List] = None
    "the list of countries with their flag,name in english, and ISO code"

    def __init__(self, translator: Optional[Translator] = None, **kwargs) -> None:
        """A language selector for sepal-ui based application.

        It displays the currently requested language (not the one used by the translator).
        When value is changed, the sepal-ui config file is updated. It is designed to be used in a AppBar component.

        .. warning:: as the component is a v.Menu to get the selected value you need to lisen to "value" instead of "v_model".

        .. versionadded:: 2.7.0

        Args:
            translator: the translator of the app, to match the used language
            kwargs (optional): any arguments for a Btn object, children will be override
        """
        # extract the available language from the translator
        # default to only en-US if no translator is set
        available_locales = (
            ["en"] if translator is None else translator.available_locales()
        )

        # extract the language information from the translator
        # if not set default to english
        code = "en" if translator is None else translator._target
        loc = self.COUNTRIES[self.COUNTRIES.code == code].squeeze()
        attr = {**self.ATTR, "src": self.FLAG.format(loc.flag), "alt": loc.name}

        kwargs.setdefault("small", True)
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

    def _get_country_items(self, locales: list) -> List[str]:
        """Get the list of countries as a list of listItem.

        Reduce the list to the available language of the module.

        Args:
            locales: list of the locales to display

        Returns:
            the list of contry widget to display in the app
        """
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

    def _on_locale_select(self, change: dict) -> None:
        """adapt the application to the newly selected language.

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
        su.set_config("locale", loc.code)

        return


class ThemeSelect(v.Btn, SepalWidget):

    THEME_ICONS: dict = {"dark": "fa-solid fa-moon", "light": "fa-solid fa-sun"}
    "the dictionnry of icons to use for each theme (used as keys)"

    theme: str = "dark"
    "the current theme of the widget (default to dark)"

    def __init__(self, **kwargs) -> None:
        """A theme selector for sepal-ui based application.

        It displays the currently requested theme (default to dark).
        When value is changed, the sepal-ui config file is updated. It is designed to be used in a AppBar component.

        .. versionadded:: 2.7.0

        Args:
            kwargs: any arguments for a Btn object, children and v_model will be override
        """
        # get the current theme name
        self.theme = get_theme()

        # set the btn parameters
        kwargs.setdefault("x_small", True)
        kwargs.setdefault("fab", True)
        kwargs.setdefault("class_", "ml-2")
        kwargs["children"] = [v.Icon(children=[self.THEME_ICONS[self.theme]])]
        kwargs["v_model"] = self.theme

        # create the btn
        super().__init__(**kwargs)

        # add some js events
        self.on_event("click", self.toggle_theme)

    def toggle_theme(self, *args) -> None:
        """Toggle the btn icon from dark to light and adapt the configuration file."""
        # use a cycle to go through the themes
        theme_cycle = cycle(self.THEME_ICONS.keys())
        next(t for t in theme_cycle if t == self.theme)
        self.theme = next(t for t in theme_cycle)

        # change icon
        self.color = "info"
        self.children[0].children = [self.THEME_ICONS[self.theme]]

        # change the paramater file
        su.set_config("theme", self.theme)

        # trigger other events by changing v_model
        self.v_model = self.theme

        return


class AppBar(v.AppBar, SepalWidget):

    toogle_button: Optional[v.Btn]
    "The btn to display or hide the drawer to the user"

    title: Optional[v.ToolbarTitle]
    "The widget containing the app title"

    locale: Optional[LocaleSelect]
    "The locale selector of all apps"

    theme = Optional[ThemeSelect]
    "The theme selector of all apps"

    def __init__(
        self,
        title: str = "SEPAL module",
        translator: Union[None, Translator] = None,
        **kwargs,
    ) -> None:
        """Custom AppBar widget with the provided title using the sepal color framework.

        Args:
            title: the title of the app
            translator: the app translator to pass to the locale selector object
            kwargs (optional): any parameters from a v.AppBar. If set, 'children' and 'app' will be overwritten.
        """
        self.toggle_button = v.Btn(
            icon=True,
            children=[
                v.Icon(class_="white--text", children=["fa-solid fa-ellipsis-v"])
            ],
        )

        self.title = v.ToolbarTitle(children=[title])

        self.locale = LocaleSelect(translator=translator)
        self.theme = ThemeSelect()

        # set the default parameters
        kwargs.setdefault("color", color.main)
        kwargs.setdefault("class_", "white--text")
        kwargs.setdefault("dense", True)
        kwargs["app"] = True
        kwargs["children"] = [
            self.toggle_button,
            self.title,
            v.Spacer(),
            self.locale,
            self.theme,
        ]

        super().__init__(**kwargs)

    def set_title(self, title: str) -> Self:
        """Set the title of the appBar.

        Args:
            title: the new app title
        """
        self.title.children = [title]

        return self


class DrawerItem(v.ListItem, SepalWidget):

    rt: Optional[ResizeTrigger] = None
    "The trigger to resize maps and other javascript object when jumping from a tile to another"

    alert: t.Bool = t.Bool(False).tag(sync=True)
    "Trait to control visibility of an alert in the drawer item"

    alert_badge: Optional[v.ListItemAction] = None
    "red circle to display in the drawer"

    tiles: Optional[List[v.Card]] = None
    "the cards of the application"

    def __init__(
        self,
        title: str,
        icon: str = "",
        card: str = "",
        href: str = "",
        model: Union[Model, None] = None,
        bind_var: str = "",
        **kwargs,
    ) -> None:
        """Custom DrawerItem using the user input.

        If a card is set the drawerItem will trigger the display of all the Tiles in the app that have the same mount_id.
        If an href is set, the drawer will open the link in a new tab.

        Args:
            title: the title of the drawer item
            icon: the full name of a mdi/fa icon
            card: the mount_id of tiles in the app
            href: the absolute link to an external web page
            model: sepalwidget model where is defined the bin_var trait
            bind_var: required when model is selected. Trait to link with 'alert' self trait parameter
            kwargs (optional): any parameter from a v.ListItem. If set, '_metadata', 'target', 'link' and 'children' will be overwritten.
        """
        # set the resizetrigger
        self.rt = rt

        icon = icon if icon else "fa-regular fa-folder"

        children = [
            v.ListItemAction(children=[v.Icon(class_="white--text", children=[icon])]),
            v.ListItemContent(
                children=[v.ListItemTitle(class_="white--text", children=[title])]
            ),
        ]

        # set default parameters
        kwargs["link"] = True
        kwargs["children"] = children
        kwargs.setdefault("input_value", False)
        if href:
            kwargs["href"] = href  # cannot be set twice anyway
            kwargs["target"] = "_blank"
            kwargs.setdefault("_metadata", None)
        elif card:
            kwargs["_metadata"] = {"card_id": card}
            kwargs.setdefault("href", None)
            kwargs.setdefault("target", None)

        # call the constructor
        super().__init__(**kwargs)

        # cannot be set as a class member because it will be shared with all
        # the other draweritems.
        self.alert_badge = v.ListItemAction(
            children=[
                v.Icon(children=["fa-solid fa-circle"], x_small=True, color="red")
            ]
        )

        if model:
            if not bind_var:
                raise Exception(
                    "You have selected a model, you need a trait to bind with drawer."
                )

            link((model, bind_var), (self, "alert"))

    @observe("alert")
    def add_notif(self, change: dict) -> None:
        """Add a notification alert to drawer."""
        if change["new"]:
            if self.alert_badge not in self.children:
                new_children = self.children[:]
                new_children.append(self.alert_badge)
                self.children = new_children
        else:
            self.remove_notif()

        return

    def remove_notif(self) -> None:
        """Remove notification alert."""
        if self.alert_badge in self.children:
            new_children = self.children[:]
            new_children.remove(self.alert_badge)

            self.children = new_children

        return

    def display_tile(self, tiles: List[v.Card]) -> Self:
        """Display the apropriate tiles when the item is clicked.

        The tile to display will be all tile in the list with the mount_id as the current object.

        Args:
            tiles: the list of all the available tiles in the app
        """
        self.tiles = tiles
        self.on_event("click", self._on_click)

        return self

    def _on_click(self, *args) -> Self:

        for tile in self.tiles:
            show = self._metadata["card_id"] == tile._metadata["mount_id"]
            tile.viz = show

        # trigger the resize event
        self.rt.resize()

        # change the current item status
        self.input_value = True

        # Remove notification
        self.remove_notif()

        return self


class NavDrawer(v.NavigationDrawer, SepalWidget):

    items: List[DrawerItem] = []
    "the list of all the drawerItem to display in the drawer"

    def __init__(
        self,
        items: List[DrawerItem] = [],
        code: str = "",
        wiki: str = "",
        issue: str = "",
        **kwargs,
    ) -> None:
        """Custom NavDrawer using the different DrawerItems of the user.

        The drawer can include links to the github page of the project for wiki, bugs and repository.

        Args:
            items: the list of all the drawerItem to display in the drawer. This items should pilote the different tile visibility
            code: the absolute link to the source code
            wiki: the absolute link the the wiki page
            issue: the absolute link to the issue tracker
            kwargs (optional) any parameter from a v.NavigationDrawer. If set, 'app' and 'children' will be overwritten.
        """
        self.items = items

        code_link = []
        if code:
            item_code = DrawerItem(
                ms.widgets.navdrawer.code, icon="fa-regular fa-file-code", href=code
            )
            code_link.append(item_code)
        if wiki:
            item_wiki = DrawerItem(
                ms.widgets.navdrawer.wiki, icon="fa-solid fa-book-open", href=wiki
            )
            code_link.append(item_wiki)
        if issue:
            item_bug = DrawerItem(
                ms.widgets.navdrawer.bug, icon="fa-solid fa-bug", href=issue
            )
            code_link.append(item_bug)

        children = [
            v.List(dense=True, children=self.items),
            v.Divider(),
            v.List(dense=True, children=code_link),
        ]

        # set default parameters
        kwargs.setdefault("v_model", True)
        kwargs["app"] = True
        kwargs.setdefault("color", color.darker)
        kwargs["children"] = children

        # call the constructor
        super().__init__(**kwargs)

        # bind the javascripts behavior
        for i in self.items:
            i.observe(self._on_item_click, "input_value")

    def display_drawer(self, toggleButton: v.Btn) -> Self:
        """Bind the drawer to the app toggleButton.

        Args:
            toggleButton: the button that activate the drawer
        """
        toggleButton.on_event("click", self._on_drawer_click)

        return self

    def _on_drawer_click(self, *args) -> Self:
        """Toggle the drawer visibility."""
        self.v_model = not self.v_model

        return self

    def _on_item_click(self, change: dict) -> Self:
        """Deactivate all the other items when on of the is activated."""
        if change["new"] is False:
            return self

        # reset all others states
        [setattr(i, "input_value", False) for i in self.items if i != change["owner"]]

        return self


class Footer(v.Footer, SepalWidget):
    def __init__(self, text: str = "", **kwargs) -> None:
        """Custom Footer with cuzomizable text.

        Not yet capable of displaying logos.

        Args:
            text: the text to display in the future
            kwargs (optional): any parameter from a v.Footer. If set ['app', 'children'] will be overwritten.
        """
        text = text if text != "" else "SEPAL \u00A9 {}".format(datetime.today().year)

        # set default parameters
        kwargs.setdefault("color", color.main)
        kwargs.setdefault("class_", "white--text")
        kwargs["app"] = True
        kwargs["children"] = [text]

        # call the constructor
        super().__init__(**kwargs)


class App(v.App, SepalWidget):

    tiles: List[v.Card] = []
    "the tiles of the app"

    appBar: Optional[AppBar] = None
    "the AppBar of the application"

    footer: Optional[Footer] = None
    "the footer of the application"

    navDrawer: Optional[NavDrawer] = None
    "the navdrawer of the application"

    content: Optional[v.Content] = None
    "the tiles organized in a fluid container"

    def __init__(
        self,
        tiles: List[v.Card] = [],
        appBar: Optional[AppBar] = None,
        footer: Optional[Footer] = None,
        navDrawer: Optional[NavDrawer] = None,
        translator: Optional[Translator] = None,
        **kwargs,
    ) -> None:
        """Custom App display with the tiles created by the user using the sepal color framework.

        Display false appBar if not filled. Navdrawer is fully optionnal.
        The drawerItem will be linked to the app tile and they will be able to control their display
        If the navdrawer exist, it will be linked to the appbar togglebtn.

        Args:
            tiles: the tiles of the app
            appBar: the appBar of the application
            footer: the footer of the application
            navDrawer: the navdrawer of the application
            translator: the translator of the app to display language informations
            kwargs (optional) any parameter from a v.App. If set, 'children' will be overwritten.
        """
        self.tiles = tiles

        app_children = []

        # create a false appBar if necessary
        if appBar is None:
            appBar = AppBar(translator=translator)
        self.appBar = appBar
        app_children.append(self.appBar)

        # add the navDrawer if existing
        if navDrawer is not None:
            # bind app tile list to the navdrawer
            [di.display_tile(tiles) for di in navDrawer.items]

            # link it with the appbar
            navDrawer.display_drawer(self.appBar.toggle_button)

            # add the drawers to the children
            self.navDrawer = navDrawer
            app_children.append(self.navDrawer)
        else:
            # remove the toggle button from the navbar
            self.appBar.toggle_button.hide()

        # add the content of the app
        self.content = v.Content(children=[v.Container(fluid=True, children=tiles)])
        app_children.append(self.content)

        # add the footer if existing
        if footer is not None:
            self.footer = footer
            app_children.append(self.footer)

        # create a negative overlay to force the background color
        bg = v.Overlay(color=color.bg, opacity=1, style_="transition:unset", z_index=-1)

        # set default parameters
        kwargs.setdefault("v_model", None)
        kwargs["children"] = [bg, *app_children]

        # call the constructor
        super().__init__(**kwargs)

        # display a warning if the set language cannot be reached
        if translator is not None:
            if translator._match is False:
                msg = ms.locale.fallback.format(
                    translator._targeted, translator._target
                )
                self.add_banner(msg, type_="error")

        # add js event
        self.appBar.locale.observe(self._locale_info, "value")
        self.appBar.theme.observe(self._theme_info, "v_model")

    def show_tile(self, name: str) -> Self:
        """Select the tile to display when the app is launched.

        Args:
            name: the mount-id of the tile(s) to display
        """
        # show the tile
        for tile in self.tiles:
            tile.viz = name == tile._metadata["mount_id"]

        # activate the drawerItem
        if self.navDrawer:
            items = (i for i in self.navDrawer.items if i._metadata is not None)
            for i in items:
                if name == i._metadata["card_id"]:
                    i.input_value = True

        return self

    @versionadded(version="2.4.1", reason="New end user interaction method")
    @versionchanged(version="2.7.1", reason="new id\_ and persistent parameters")
    def add_banner(
        self,
        msg: str = "",
        type_: str = "info",
        id_=None,
        persistent: bool = True,
        **kwargs,
    ) -> Self:
        r"""Display a snackbar object on top of the app.

        Used to communicate development information to end user (release date, known issues, beta version). The alert is dissmisable and prominent.

        Args:
            msg: Message to display in application banner. default to nothing
            type\_: Used to display an appropiate banner color. fallback to "info".
            id\_: unique banner identificator.
            persistent: Whether to close automatically based on the lenght of message (False) or make it indefinitely open (True). Overridden if timeout duration is set.
            \*\*kwargs: any arguments of the sw.Banner constructor. if set, 'children' will be overwritten.
        """
        # the Banner was previously an Alert. for compatibility we accept the type parameter
        type_ = kwargs.pop("type", type_)

        # the banner will be piled up from the first to the latest.
        # only the first one is shown
        # dismissed banner are remove from the children

        # extract the banner from the app children
        children, banner_list = [], []
        for e in self.content.children.copy():
            dst = banner_list if isinstance(e, Banner) else children
            dst.append(e)

        # only set viz to true if it's the first one
        viz = False if len(banner_list) > 0 else True

        # create the baner and interactions
        w_bnr = Banner(msg, type_, id_, persistent, viz=viz, **kwargs)
        banner_list += [w_bnr]

        # display the number of banner in queue
        banner_list[0].set_btn(len(banner_list) - 1)

        # place everything back in the app chldren list
        self.content.children = banner_list + children

        # add interaction at the end
        w_bnr.observe(self._remove_banner, "v_model")

        return self

    def _locale_info(self, change: dict) -> None:
        """Display information about the locale change."""
        if change["new"] != "":
            msg = ms.locale.change.format(change["new"])
            self.add_banner(msg)

        return

    def _theme_info(self, change: dict) -> None:
        """Display information about the theme change."""
        if change["new"] != "":
            msg = ms.theme.change.format(change["new"])
            self.add_banner(msg)

        return

    def _remove_banner(self, change: dict) -> None:
        """Remove banner and adapt display of the others.

        Adapt the banner display so that the first one is the only one shown displaying the number of other banner in the queue
        """
        if change["new"] is False:

            # extract the banner from the app children
            children, banner_list = [], []
            for e in self.content.children.copy():
                dst = banner_list if isinstance(e, Banner) else children
                dst.append(e)

            # remove the banner from the list
            banner_list.remove(change["owner"])

            # change the visibility of the widgets
            [setattr(b, "viz", i == 0) for i, b in enumerate(banner_list)]

            # set the btn of the the first element if possible
            len(banner_list) == 0 or banner_list[0].set_btn(len(banner_list) - 1)

            # place everything back in the app chldren list
            self.content.children = banner_list + children

        return
