"""Custom Map app layout for SEPAL ui Map interfaces."""

import json
import logging
from pathlib import Path
from typing import Optional

import ipyvuetify as v
import pandas as pd
from ipywidgets import DOMWidget, jsdlink, link
from ipywidgets.widgets.widget import widget_serialization
from traitlets import Bool, Dict, HasTraits, Instance, Int, List, Unicode

from sepal_ui.scripts import utils as su
from sepal_ui.translator import Translator

logger = logging.getLogger("sepalui.vue_app")


class MapApp(v.VuetifyTemplate):

    template_file = Unicode(str(Path(__file__).parents[1] / "sepalwidgets/vue/MapApp.vue")).tag(
        sync=True
    )

    app_title = Unicode("Map Application").tag(sync=True)
    app_icon = Unicode("mdi-earth").tag(sync=True)
    repo_url = Unicode("").tag(sync=True)
    docs_url = Unicode("").tag(sync=True)

    dialog_width = Int(800).tag(sync=True)
    dialog_fullscreen = Bool(False).tag(sync=True)

    main_map = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)
    theme_toggle = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)
    language_selector = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)
    right_panel = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)

    # Right panel state tracking
    right_panel_open = Bool(False).tag(sync=True)
    right_panel_width = Int(300).tag(sync=True)

    # Right panel configuration
    right_panel_config = Dict(
        default_value={
            "title": "Extra Content",
            "icon": "mdi-widgets",
            "width": 300,
            "description": "",
            "toggle_icon": "mdi-chevron-left",
        }
    ).tag(sync=True)

    right_panel_content = List(
        Dict(
            {
                "title": Unicode(),
                "icon": Unicode(),
                "content": List(Instance(DOMWidget)),
                "divider": Bool(),
                "description": Unicode(),
            }
        ),
        default_value=[],
    ).tag(sync=True, **widget_serialization)

    steps_data = List(
        Dict(
            {
                "id": Int(),
                "name": Unicode(),
                "icon": Unicode(),
                "display": Unicode(),
                "right_panel_action": Unicode(),
                "content": List(Instance(DOMWidget)),
                "content_enabled": Bool(),
                "actions": List(),
                "width": Int(),
                "height": Int(),
            }
        )
    ).tag(sync=True, **widget_serialization)

    initial_step = Int(allow_none=True).tag(sync=True)
    current_step = Int(allow_none=True).tag(sync=True)
    step_open = Bool(False).tag(sync=True)

    def __init__(
        self,
        theme_toggle: "ThemeToggle" = None,
        initial_step: Optional[int] = None,
        model: Optional[HasTraits] = None,
        **kwargs,
    ):
        """Instantiate the MapApp class.

        Parameters
        ----------
        theme_toggle : ThemeToggle, optional
            Theme toggle widget
        initial_step : int, optional
            Initial step to display
        model : HasTraits, optional
            Model to bind with. If provided, will automatically link matching traitlets
        **kwargs
            Additional parameters
        """
        self.theme_toggle = theme_toggle
        self._model = model
        self._model_links = []  # Store links for cleanup

        # Create right panel from parameters if content or config is provided
        right_panel = None
        if kwargs.get("right_panel_content") or kwargs.get("right_panel_config"):
            config = kwargs.get("right_panel_config", {})
            content_data = kwargs.get("right_panel_content", [])

            right_panel = RightPanel(config=config, content_data=content_data)

            # Check if right_panel_open was specified and apply it
            if "right_panel_open" in kwargs:
                right_panel.is_open = kwargs["right_panel_open"]

        kwargs["right_panel"] = [right_panel] if right_panel else []

        # Set up right panel state tracking
        if right_panel:
            kwargs["right_panel_open"] = right_panel.is_open
            kwargs["right_panel_width"] = right_panel.config.get("width", 300)

        kwargs["language_selector"] = kwargs.get("language_selector", [LocaleSelect()])

        # Handle initial step configuration
        if initial_step is not None:
            kwargs["initial_step"] = initial_step
            kwargs["current_step"] = initial_step

        super().__init__(**kwargs)

        # Set up right panel state observation after initialization
        if right_panel:
            right_panel.observe(self._on_right_panel_change, "is_open")
            right_panel.observe(self._on_right_panel_config_change, "config")

        # Set up automatic model binding if model is provided
        if self._model is not None:
            self._setup_model_binding()

    def _setup_model_binding(self):
        """Set up automatic two-way binding with the provided model.

        This method automatically links matching traitlets between MapApp and the model.
        """
        logger.info("Setting up model binding...")
        if self._model is None:
            return

        # Get all traitlet names from both objects
        app_traits = set(self.trait_names())
        model_traits = set(self._model.trait_names())

        common_traits = app_traits.intersection(model_traits)

        # Set up bidirectional links for common traits
        for trait_name in common_traits:
            if trait_name.startswith("_") or trait_name in [
                "template_file",
                "main_map",
                "theme_toggle",
                "language_selector",
                "right_panel",
                "steps_data",
                "right_panel_content",
            ]:
                continue

            try:
                model_link = link((self, trait_name), (self._model, trait_name))
                self._model_links.append(model_link)
            except Exception as e:
                logger.warning(f"⚠ Could not link {trait_name}: {e}")

    def unlink_model(self):
        """Remove all model links and cleanup."""
        for model_link in self._model_links:
            model_link.unlink()
        self._model_links.clear()
        self._model = None

    def set_model(self, model: HasTraits):
        """Set or change the bound model.

        Parameters
        ----------
        model : HasTraits
            New model to bind with
        """
        # Cleanup existing links
        self.unlink_model()

        # Set new model and create links
        self._model = model
        if model is not None:
            self._setup_model_binding()

    def vue_handle_right_panel_action(self, action):
        """Handle right panel actions from step activation."""
        if self.right_panel and len(self.right_panel) > 0:
            panel = self.right_panel[0]
            if action == "open":
                panel.is_open = True
            elif action == "close":
                panel.is_open = False
            elif action == "toggle":
                panel.is_open = not panel.is_open

    def vue_handle_step_change(self, step_id, is_open):
        """Handle step activation/deactivation from Vue component.

        Parameters
        ----------
        step_id : int
            The ID of the step being changed
        is_open : bool
            Whether the step is being opened or closed
        """
        self.current_step = step_id if is_open else None
        self.step_open = is_open

    def vue_handle_step_activation(self, step_id):
        """Handle step activation from Vue component.

        Parameters
        ----------
        step_id : int
            The ID of the step being activated
        """
        self.current_step = step_id
        self.step_open = True

    def vue_handle_step_deactivation(self):
        """Handle step deactivation from Vue component."""
        self.current_step = None
        self.step_open = False

    def _on_right_panel_change(self, change):
        """Update the right panel state when it changes."""
        self.right_panel_open = change["new"]

    def _on_right_panel_config_change(self, change):
        """Update the right panel width when config changes."""
        new_config = change["new"]
        if "width" in new_config:
            self.right_panel_width = new_config["width"]


class ThemeToggle(v.VuetifyTemplate):

    template_file = Unicode(str(Path(__file__).parents[1] / "sepalwidgets/vue/Theming.vue")).tag(
        sync=True
    )

    dark = Bool(None, allow_none=True).tag(sync=True)
    enable_auto = Bool(True).tag(sync=True)
    on_icon = Unicode("mdi-weather-night").tag(sync=True)
    off_icon = Unicode("mdi-white-balance-sunny").tag(sync=True)
    auto_icon = Unicode("mdi-auto-fix").tag(sync=True)


class RightPanel(v.VuetifyTemplate):

    template_file = Unicode(str(Path(__file__).parents[1] / "sepalwidgets/vue/RightPanel.vue")).tag(
        sync=True
    )

    is_open = Bool(False).tag(sync=True)
    disabled = Bool(False).tag(sync=True)

    config = Dict(
        default_value={
            "title": "Extra Content",
            "icon": "mdi-widgets",
            "width": 300,
            "description": "",
            "toggle_icon": "mdi-chevron-left",
        }
    ).tag(sync=True)

    content_data = List(
        Dict(
            {
                "title": Unicode(),
                "icon": Unicode(),
                "content": List(Instance(DOMWidget)),
                "divider": Bool(),
                "description": Unicode(),
            }
        ),
        default_value=[],
    ).tag(sync=True, **widget_serialization)

    def __init__(self, **kwargs):
        """Initialize RightPanel with event handlers."""
        super().__init__(**kwargs)

    def vue_panel_state_changed(self, state):
        """Handle panel state changes from Vue component."""
        self.is_open = state


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
