from ipywidgets import HTML
from traitlets import Unicode
from IPython.display import display
import ipyvuetify as v 

# change vuetify theming 
v.theme.dark = True
v.theme.themes.dark.primary = "#B3842E"
v.theme.themes.dark.accent = "#a1458e"
v.theme.themes.dark.secondary = "#324a88"
v.theme.themes.dark.success = "#3F802A"
v.theme.themes.dark.info = "#79B1C9"
v.theme.themes.dark.warning = "#b8721d"
v.theme.themes.dark.error = "#A63228"

#fixed colors 
sepal_main = '#24221F'
sepal_darker = '#1a1a1a'


# Fixed styles to avoid leaflet maps overlap sepal widgets

class Styles(v.VuetifyTemplate):

    template=Unicode("""
    <style>
        .leaflet-pane {
            z-index : 2 !important;
        }
        .leaflet-top, .leaflet-bottom {
            z-index : 2 !important;
        }
        main.v-content {
            padding-top: 0px !important;
        }
    </style>
    """).tag(sync=True)
    
styles=Styles()
display(styles)

COMPONENTS = {

    'PROGRESS_BAR':{
        'color':'indigo',
    }
}

ICON_TYPES = {
    # Used for folders
    '':{ 
        'color':'amber',
        'icon':'mdi-folder-outline'
    },
    '.csv':{
        'color':'green accent-4',
        'icon':'mdi-border-all'
    },
    '.txt':{
        'color':'green accent-4',
        'icon':'mdi-border-all'
    },
    '.tif':{
        'color':'deep-purple',
        'icon':'mdi-image-outline'
    },
    '.tiff':{
        'color':'deep-purple',
        'icon':'mdi-image-outline'
    },
    '.shp':{
        'color':'deep-purple',
        'icon':'mdi-vector-polyline'
    },
    'DEFAULT':{
        'color':'light-blue',
        'icon':'mdi-file-outline'
    },
    # Icon for parent folder
    'PARENT':{ 
        'color':'white',
        'icon':'mdi-folder-upload-outline'
    },

}
