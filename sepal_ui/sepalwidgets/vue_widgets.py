"""Custom FileInput widget that leverages vuetify templates and handles both local and remote files (sepal)."""

from pathlib import Path

import ipyvuetify as v
from ipywidgets import DOMWidget
from ipywidgets.widgets.widget import widget_serialization
from traitlets import Instance, Int, List, Unicode


class Tabs(v.VuetifyTemplate):

    template_file = Unicode(str(Path(__file__).parent / "vue/Tabs.vue")).tag(sync=True)
    titles = List(Unicode()).tag(sync=True)
    content = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)
    current = Int().tag(sync=True)
