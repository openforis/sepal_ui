"""Custom Map app layout for SEPAL ui Map interfaces."""

from pathlib import Path

import ipyvuetify as v
from ipywidgets import DOMWidget
from ipywidgets.widgets.widget import widget_serialization
from traitlets import Bool, Dict, Instance, Int, List, Unicode


class MapApp(v.VuetifyTemplate):

    template_file = Unicode(str(Path(__file__).parents[1] / "sepalwidgets/vue/MapApp.vue")).tag(
        sync=True
    )

    repo_url = Unicode("").tag(sync=True)
    app_title = Unicode("Map Application").tag(sync=True)
    main_map = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)
    steps_content = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)
    theme_toggle = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)

    steps_data = List(
        Dict(
            {
                "id": Int(),
                "name": Unicode(),
                "icon": Unicode(),
                "display": Unicode(),
            }
        )
    ).tag(sync=True)

    def __init__(self, **kwargs):
        """Instantiate the MapApp class."""
        kwargs["theme_toggle"] = [ThemeToggle()]
        super().__init__(**kwargs)


class ThemeToggle(v.VuetifyTemplate):

    template_file = Unicode(str(Path(__file__).parents[1] / "sepalwidgets/vue/Theming.vue")).tag(
        sync=True
    )

    dark = Bool(None, allow_none=True).tag(sync=True)
    enable_auto = Bool(True).tag(sync=True)
    on_icon = Unicode("mdi-weather-night").tag(sync=True)
    off_icon = Unicode("mdi-weather-sunny").tag(sync=True)
    auto_icon = Unicode("mdi-auto-fix").tag(sync=True)
