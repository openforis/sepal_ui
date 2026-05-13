"""MapAppShell — the VuetifyTemplate that renders MapAppShell.vue.

This widget is an implementation detail of MapAppComponent. Its trait
shape mirrors the props of `pysepal/sepalwidgets/vue/MapAppShell.vue`.
Callers should use `MapAppComponent` rather than this class directly.
"""

from __future__ import annotations

from pathlib import Path

import ipyvuetify as v
from ipywidgets import DOMWidget
from ipywidgets.widgets.widget import widget_serialization
from traitlets import Any, Bool, Dict, Instance, Int, List, Tuple, Unicode

_VUE_FILE = Path(__file__).resolve().parents[3] / "sepalwidgets" / "vue" / "MapAppShell.vue"


class MapAppShell(v.VuetifyTemplate):
    """VuetifyTemplate backing MapAppComponent."""

    template_file = Unicode(str(_VUE_FILE)).tag(sync=True)

    app_title = Unicode("Map Application").tag(sync=True)
    app_icon = Unicode("mdi-earth").tag(sync=True)
    repo_url = Unicode("").tag(sync=True)
    docs_url = Unicode("").tag(sync=True)

    dialog_width = Int(800).tag(sync=True)
    dialog_fullscreen = Bool(False).tag(sync=True)

    main_map = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)
    theme_toggle = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)
    language_selector = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)

    # Right panel — rendered inline by Vue from JSON + per-section widgets.
    right_panel_config = Dict(default_value={}).tag(sync=True)
    right_panel_sections = List(default_value=[]).tag(sync=True)
    right_panel_content_widgets = List(Instance(DOMWidget)).tag(sync=True, **widget_serialization)
    right_panel_open = Bool(False).tag(sync=True)
    right_panel_width = Int(300).tag(sync=True)

    # Steps + active content widget (Python swaps in/out).
    steps_data = List(default_value=[]).tag(sync=True)
    active_step_content = Instance(DOMWidget, allow_none=True, default_value=None).tag(
        sync=True, **widget_serialization
    )
    initial_step = Int(allow_none=True, default_value=None).tag(sync=True)
    current_step = Int(allow_none=True, default_value=None).tag(sync=True)
    step_open = Bool(False).tag(sync=True)

    # `with MapAppComponent(): ...` children slot.
    children_slot = Instance(DOMWidget, allow_none=True, default_value=None).tag(
        sync=True, **widget_serialization
    )

    # Last action event fired from a step dialog footer button.
    # Shape: (step_id, event_name, counter). Counter is monotonically
    # incremented so two identical events still trigger observers.
    last_action_event = Tuple(default_value=(-1, "", 0))

    # Python callbacks (not synced to JS). Reacton's `.element()` only
    # forwards declared traits, so these are exposed as `Any` traits.
    on_step_change = Any(default_value=None, allow_none=True)
    on_step_action = Any(default_value=None, allow_none=True)
    on_right_panel_toggle = Any(default_value=None, allow_none=True)

    # External links + sidebar telemetry.
    external_links = List(default_value=[]).tag(sync=True)
    is_pinned = Bool(True).tag(sync=True)
    drawer_width = Int(320).tag(sync=True)
    window_width = Int(0).tag(sync=True)
    window_height = Int(0).tag(sync=True)

    def __init__(self, **kwargs) -> None:
        """Initialize the shell with optional trait overrides."""
        self._action_counter = 0
        super().__init__(**kwargs)

    # ----- Vue → Python events -------------------------------------------------

    def vue_handle_step_change(self, step_id, is_open):
        """Forward Vue step-change events into traits + callback."""
        self.current_step = int(step_id) if is_open else None
        self.step_open = bool(is_open)
        if self.on_step_change is not None:
            self.on_step_change(self.current_step, self.step_open)

    def vue_handle_step_activation(self, step_id):
        """Forward Vue step activation."""
        self.current_step = int(step_id)
        self.step_open = True
        if self.on_step_change is not None:
            self.on_step_change(self.current_step, True)

    def vue_handle_step_deactivation(self, *_args):
        """Forward Vue step deactivation."""
        self.current_step = None
        self.step_open = False
        if self.on_step_change is not None:
            self.on_step_change(None, False)

    def vue_handle_step_action(self, step_id, event):
        """Forward a step's footer action button click.

        Updates the `last_action_event` trait (so Solara observers fire)
        and also invokes the legacy `on_step_action` callback when set.
        """
        self._action_counter += 1
        self.last_action_event = (int(step_id), str(event), self._action_counter)
        if self.on_step_action is not None:
            self.on_step_action(int(step_id), str(event))

    def vue_handle_right_panel_action(self, action):
        """Open / close / toggle the right panel."""
        if action == "open":
            self.right_panel_open = True
        elif action == "close":
            self.right_panel_open = False
        elif action == "toggle":
            self.right_panel_open = not self.right_panel_open
        if self.on_right_panel_toggle is not None:
            self.on_right_panel_toggle(self.right_panel_open)

    def vue_set_right_panel_open(self, value):
        """Sync right-panel state from Vue (v-model)."""
        new_value = bool(value)
        if new_value != self.right_panel_open:
            self.right_panel_open = new_value
            if self.on_right_panel_toggle is not None:
                self.on_right_panel_toggle(new_value)

    def vue_set_drawer_width(self, width):
        """Receive the real drawer pixel width from Vue."""
        try:
            self.drawer_width = int(width)
        except (TypeError, ValueError):
            pass

    def vue_set_window_size(self, size):
        """Receive the real browser window size from Vue."""
        try:
            self.window_width = int(size.get("w", 0))
            self.window_height = int(size.get("h", 0))
        except (TypeError, ValueError, AttributeError):
            pass
