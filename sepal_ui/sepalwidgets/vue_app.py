"""Custom Map app layout for SEPAL ui Map interfaces."""

import json
from pathlib import Path
from typing import Optional

import ipyvuetify as v
import pandas as pd
from ipywidgets import DOMWidget, jsdlink
from ipywidgets.widgets.widget import widget_serialization
from traitlets import Bool, Dict, Instance, Int, List, Unicode

from sepal_ui.scripts import utils as su
from sepal_ui.translator import Translator


class MapApp(v.VuetifyTemplate):

    template_file = Unicode(str(Path(__file__).parents[1] / "sepalwidgets/vue/MapApp.vue")).tag(
        sync=True
    )

    repo_url = Unicode("").tag(sync=True)
    app_title = Unicode("Map Application").tag(sync=True)
    app_icon = Unicode("mdi-earth").tag(sync=True)
    open_dialog = Bool(False).tag(sync=True)
    dialog_width = Int(800).tag(sync=True)
    right_panel_open = Bool(False).tag(sync=True)

    main_map = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)
    theme_toggle = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)
    language_selector = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)

    # Remove old extra_content - replaced by extra_content_data
    extra_content_config = Dict(
        {
            "title": Unicode(),
            "icon": Unicode(),
            "width": Int(),
            "description": Unicode(),
            "toggle_icon": Unicode(),
        }
    ).tag(sync=True)

    steps_data = List(
        Dict(
            {
                "id": Int(),
                "name": Unicode(),
                "icon": Unicode(),
                "display": Unicode(),
                "right_panel_action": Unicode(),
                "content": List(Instance(DOMWidget)),
            }
        )
    ).tag(sync=True, **widget_serialization)

    extra_content_data = List(
        Dict(
            {
                "title": Unicode(),
                "icon": Unicode(),
                "content": List(Instance(DOMWidget)),
                "divider": Bool(),
                "description": Unicode(),
            }
        )
    ).tag(sync=True, **widget_serialization)

    def __init__(self, theme_toggle: "ThemeToggle" = None, **kwargs):
        """Instantiate the MapApp class."""
        self.theme_toggle = theme_toggle

        kwargs["language_selector"] = kwargs.get("language_selector", [LocaleSelect()])
        super().__init__(**kwargs)


class ThemeToggle(v.VuetifyTemplate):

    template_file = Unicode(str(Path(__file__).parents[1] / "sepalwidgets/vue/Theming.vue")).tag(
        sync=True
    )

    dark = Bool(None, allow_none=True).tag(sync=True)
    enable_auto = Bool(True).tag(sync=True)
    on_icon = Unicode("mdi-weather-night").tag(sync=True)
    off_icon = Unicode("mdi-white-balance-sunny").tag(sync=True)
    auto_icon = Unicode("mdi-auto-fix").tag(sync=True)


class LocaleSelect(v.VuetifyTemplate):

    template_file = Unicode(
        str(Path(__file__).parents[1] / "sepalwidgets/vue/LocaleSelect.vue")
    ).tag(sync=True)

    COUNTRIES: pd.DataFrame = pd.read_parquet(Path(__file__).parents[1] / "data" / "locale.parquet")
    available_locales = List([{"code": "en", "name": "English", "flag": "gb"}]).tag(sync=True)
    selected_locale = Unicode("en").tag(sync=True)
    value = Unicode().tag(sync=True)

    def __init__(self, translator: Optional[Translator] = None, **kwargs):
        """Instantiate the LocaleSelect class."""
        super().__init__(**kwargs)

        available_locales = ["en"] if translator is None else translator.available_locales()
        available_locales = self.COUNTRIES[self.COUNTRIES.code.isin(available_locales)]
        self.available_locales = json.loads(available_locales.to_json(orient="records"))

        # TODO: consider removing this, I'm not sure if an app is using the value
        jsdlink((self, "selected_locale"), (self, "value"))

        self.observe(self._on_locale_select, "selected_locale")

    def _on_locale_select(self, change: dict) -> None:
        """adapt the application to the newly selected language.

        Display the new flag and country code on the widget btn
        change the value in the config file
        """
        if not change["new"]:
            return

        # get the line in the locale dataframe
        loc = self.COUNTRIES[self.COUNTRIES.code == change["new"]].squeeze()

        # change the parameter file
        su.set_config("locale", loc.code)

        return
