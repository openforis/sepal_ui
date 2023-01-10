from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Tuple

import ipyvuetify as v
from IPython.display import display
from traitlets import Bool, HasTraits, Unicode, observe

import sepal_ui.scripts.utils as su
from sepal_ui.conf import config

################################################################################
# access the folders where style information is stored (layers, widgets)
#

# the colors are set using tables as follow.
# 1 (True): dark theme
# 0 (false): light theme
JSON_DIR: Path = Path(__file__).parent / "json"
"The path to the json style folder"

CSS_DIR: Path = Path(__file__).parent / "css"
"The path to the css style folder"

JS_DIR: Path = Path(__file__).parent / "js"
"The path to the js style folder"

################################################################################
# define all the colors taht we want to use in the theme
#

DARK_THEME: Dict[str, str] = {
    "primary": "#b3842e",
    "accent": "#a1458e",
    "secondary": "#324a88",
    "success": "#3f802a",
    "info": "#79b1c9",
    "warning": "#b8721d",
    "error": "#a63228",
    "main": "#24221f",  # Are not traits
    "darker": "#1a1a1a",  # Are not traits
    "bg": "#121212",  # Are not traits
    "menu": "#424242",  # Are not traits
}
"colors used for the dark theme"

LIGHT_THEME: Dict[str, str] = {
    "primary": v.theme.themes.light.primary,
    "accent": v.theme.themes.light.accent,
    "secondary": v.theme.themes.light.secondary,
    "success": v.theme.themes.light.success,
    "info": v.theme.themes.light.info,
    "warning": v.theme.themes.light.warning,
    "error": v.theme.themes.light.error,
    "main": "#2e7d32",
    "darker": "#005005",
    "bg": "#FFFFFF",
    "menu": "#FFFFFF",
}
"colors used for the light theme"

TYPES: Tuple[str, ...] = (
    "info",
    "primary",
    "secondary",
    "accent",
    "error",
    "success",
    "warning",
    "anchor",
)
"The different types defined by ipyvuetify"

################################################################################
# define classes and method to make the application resonsive
#


def get_theme() -> str:
    """
    Get theme name from the config file (default to dark).

    Returns
    -------
        The theme to use
    """
    return config.get("sepal-ui", "theme", fallback="dark")


class SepalColor(HasTraits, SimpleNamespace):

    _dark_theme: Bool = Bool(True if get_theme() == "dark" else False).tag(sync=True)
    "Whether to use dark theme or not. By changing this value, the theme value will be stored in the conf file. Is only intended to be accessed in development mode."

    new_colors: dict = {}
    "Dictionary with name:color structure."

    @observe("_dark_theme")
    def __init__(self, *_, **new_colors) -> None:
        """
        Custom simple name space to store and access to the sepal_ui colors and with a magic method to display theme.

        Args:
        ----
            **new_colors (optional): the new colors to set in hexadecimal as a dict (experimetal)
        """
        # set vuetify theme
        v.theme.dark = self._dark_theme

        # Get get current theme name
        self.theme_name = "dark" if self._dark_theme else "light"

        # Save "new" theme in configuration file
        su.set_config("theme", self.theme_name)

        self.kwargs = DARK_THEME if self._dark_theme else LIGHT_THEME
        self.kwargs = new_colors or self.kwargs

        # Even if the theme.themes.dark_theme trait could trigger the change on all elms
        # we have to replace the default values everytime:
        theme = getattr(v.theme.themes, self.theme_name)

        # TODO: Would be awesome to find a way to create traits for the new colors and
        # assign them here directly
        [setattr(theme, color_name, color) for color_name, color in self.kwargs.items()]

        # Now instantiate the namespace
        SimpleNamespace.__init__(self, **self.kwargs)
        HasTraits.__init__(self)

        return

    def _repr_html_(self, *_) -> str:
        """Rich display of the color palette in an HTML frontend."""
        s = 60
        html = f"<h3>Current theme: {self.theme_name}</h3><table>"
        items = {k: v for k, v in self.kwargs.items()}.items()

        for name, color in items:
            c = su.to_colors(color)
            html += f"""
            <th>
                <svg width='{s}' height='{s}'>
                    <rect width='{s}' height='{s}' style='fill:{c};
                    stroke-width:1;stroke:rgb(255,255,255)'/>
                </svg>
            </th>
            """

        html += "</tr><tr>"
        html += "".join([f"<td>{name}</br>{color}</td>" for name, color in items])
        html += "</tr></table>"

        return html


class Styles(v.VuetifyTemplate):
    """
    Fixed styles to fix display issues in the lib:

    - avoid leaflet maps overlap sepal widgets
    - remove shadow of widget-control
    - remove padding of the main content
    - load fontawsome as a resource
    - ensure that tqdm bars are using a transparent background when displayed in an alert
    - correct items z-index
    """

    css = (CSS_DIR / "custom.css").read_text()
    cdn = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css"
    key = "sha512-MV7K8+y+gLIBoVD59lQIYicR65iaqukzvf/nwasF0nqhPay5w/9lJmVM2hMDcnK1OnMGCdVK+iQrJ7lzPJQd1w=="
    template: Unicode = Unicode(
        f"<style>{css}</style>"
        f'<link rel="stylesheet" href="{cdn}" integrity="{key}" crossorigin="anonymous", refferpolicy="no-referrer"/>'
    ).tag(sync=True)
    "The trait embeding the maps style"


styles = Styles()
display(styles)
