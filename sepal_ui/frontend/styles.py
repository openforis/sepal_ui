from traitlets import Unicode
from IPython.display import display
import ipyvuetify as v

# change vuetify theming
v.theme.dark = True

# set the colors for the dark theme
v.theme.themes.dark.primary = "#B3842E"
v.theme.themes.dark.accent = "#a1458e"
v.theme.themes.dark.secondary = "#324a88"
v.theme.themes.dark.success = "#3F802A"
v.theme.themes.dark.info = "#79B1C9"
v.theme.themes.dark.warning = "#b8721d"
v.theme.themes.dark.error = "#A63228"

# fixed colors
sepal_main = "#24221F"
sepal_darker = "#1a1a1a"

# set the background
bg_color = "#121212" if v.theme.dark else "#fff"


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

COMPONENTS = {
    "PROGRESS_BAR": {
        "color": "indigo",
    }
}

# default styling of the aoi layer
AOI_STYLE = {
    "stroke": True,
    "color": v.theme.themes.dark.success,
    "weight": 2,
    "opacity": 1,
    "fill": True,
    "fillColor": v.theme.themes.dark.success,
    "fillOpacity": 0.4,
}


_folder = {"color": "amber", "icon": "far fa-folder"}
_table = {"color": "green accent-4", "icon": "far fa-table"}
_vector = {"color": "deep-purple", "icon": "far fa-vector-square"}
_other = {"color": "light-blue", "icon": "far fa-file"}
_parent = {"color": "white", "icon": "far fa-folder-open"}
_image = {"color": "deep-purple", "icon": "far fa-image"}

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
