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
    Fixed styles to avoid leaflet maps overlap sepal widgets
    """

    template = Unicode(
        """
        <style>
            .leaflet-pane {z-index : 2 !important;}
            .leaflet-top, .leaflet-bottom {z-index : 2 !important;}
            main.v-content {padding-top: 0px !important;}
        </style>
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


_folder = {"color": "amber", "icon": "mdi-folder-outline"}
_table = {"color": "green accent-4", "icon": "mdi-border-all"}
_vector = {"color": "deep-purple", "icon": "mdi-vector-polyline"}
_other = {"color": "light-blue", "icon": "mdi-file-outline"}
_parent = {"color": "white", "icon": "mdi-folder-upload-outline"}
_image = {"color": "deep-purple", "icon": "mdi-image-outline"}

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
