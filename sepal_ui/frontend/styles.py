from traitlets import Unicode
from IPython.display import display
import ipyvuetify as v

# set the colors for the dark theme
v.theme.themes.dark.primary = "#b3842e"
v.theme.themes.dark.accent = "#a1458e"
v.theme.themes.dark.secondary = "#324a88"
v.theme.themes.dark.success = "#3f802a"
v.theme.themes.dark.info = "#79b1c9"
v.theme.themes.dark.warning = "#b8721d"
v.theme.themes.dark.error = "#a63228"

# fixed colors for drawer and appbar
v.theme.themes.dark.main = "#24221f"
v.theme.themes.light.main = "#2e7d32"
v.theme.themes.dark.darker = "#1a1a1a"
v.theme.themes.light.darker = "#005005"

# set the background
v.theme.themes.dark.bg_color = "#121212"
v.theme.themes.light.bg_color = "#fff"

# set a specific color for menus
v.theme.themes.dark.menu = "#424242"
v.theme.themes.light.menu = "#fff"


class Styles(v.VuetifyTemplate):
    """
    Fixed styles to fix display issues in the lib:

    - avoid leaflet maps overlap sepal widgets
    - remove shadow of widget-control
    - remove padding of the main content
    - load fontawsome as a resource
    """

    template = Unicode(
        """
        <style>
            .leaflet-pane {z-index : 2 !important;}
            .leaflet-top, .leaflet-bottom {z-index : 2 !important;}
            .leaflet-widgetcontrol {box-shadow: none}
            main.v-content {padding-top: 0px !important;}
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"/>
    """
    ).tag(sync=True)
    "Unicode: the trait embeding the maps style"


styles = Styles()
display(styles)

# default styling of the aoi layer
AOI_STYLE = {
    "stroke": True,
    "color": "grey",
    "weight": 2,
    "opacity": 1,
    "fill": True,
    "fillColor": "grey",
    "fillOpacity": 0.4,
}

# the colors are set as follow.
# 1 (True): dark theme
# 0 (false): light theme
# This will need to be changed if we want to support more than 2 theme
COMPONENTS = {
    "PROGRESS_BAR": {
        "color": ["#2196f3", "#3f51b5"],
    }
}

_folder = {"color": ["#ffca28", "#ffc107"], "icon": "far fa-folder"}
_table = {"color": ["#4caf50", "#00c853"], "icon": "far fa-table"}
_vector = {"color": ["#9c27b0", "#673ab7"], "icon": "far fa-vector-square"}
_other = {"color": ["#00bcd4", "#03a9f4"], "icon": "far fa-file"}
_parent = {"color": ["#424242", "#ffffff"], "icon": "far fa-folder-open"}
_image = {"color": ["#9c27b0", "#673ab7"], "icon": "far fa-image"}

ICON_TYPES = {
    "": _folder,
    ".csv": _table,
    ".txt": _table,
    ".tif": _image,
    ".tiff": _image,
    ".vrt": _image,
    ".shp": _vector,
    ".geojson": _vector,
    "DEFAULT": _other,
    "PARENT": _parent,
}
