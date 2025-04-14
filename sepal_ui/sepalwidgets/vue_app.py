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

    main_map = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)
    steps_content = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)
    theme_toggle = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)
    language_selector = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)

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
        kwargs["language_selector"] = [LocaleSelect()]
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
