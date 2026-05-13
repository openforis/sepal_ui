"""Minimal demo of the Solara-native `MapAppComponent`.

Run with:

    eval "$(micromamba shell hook --shell bash)" && micromamba activate pysepal
    solara run pysepal/templates/solara/solara_map_app/mapapp_component_demo.py

Showcases:
- `with MapAppComponent(...): ...` for floating overlay content.
- Typed `StepConfig` and `PanelSection`.
- Reactive `current_step` and `right_panel_open` props.
- Step "action" buttons firing through `on_step_action`.
- External link tiles auto-rendered in the drawer footer.

This template does NOT require GEE/SEPAL sessions — it is the smallest
useful example of the new API. For a session-backed app, see `app.py`.
"""

import logging

import solara

from pysepal.solara import (
    MapAppComponent,
    NotificationProvider,
    get_current_theme_state,
    setup_solara_server,
    setup_theme_colors,
    use_notifications,
)
from pysepal.solara.components.layout import (
    ExternalLink,
    PanelSection,
    RightPanelConfig,
    StepAction,
    StepConfig,
)

logger = logging.getLogger("SEPALUI.mapapp_component_demo")

setup_solara_server()


@solara.component
def AoiStep():
    """Render fn used by the AOI step (display='step')."""
    with solara.Card(title="Area of Interest"):
        solara.Markdown(
            "This is the AOI step. Pick a method, hit submit, and the "
            "selection appears on the map."
        )
        solara.Button("Submit AOI", color="primary")


@solara.component
def SettingsDialog():
    """Render fn used by the Settings step (display='dialog')."""
    solara.Markdown("Adjust the analysis parameters and click **Apply**.")
    solara.SliderInt("Threshold", value=50, min=0, max=100)
    solara.SliderFloat("Smoothing", value=0.3, min=0.0, max=1.0)


@solara.component
def LayerControls():
    """Render fn for the right panel's Layers section."""
    with solara.Column():
        solara.Markdown("**Active layers**")
        solara.Switch(label="NDVI", value=True)
        solara.Switch(label="True color", value=False)


@solara.component
def LegendSection():
    """Render fn for the right panel's Legend section."""
    solara.Markdown("Color ramp legends would appear here.")


@solara.component
def Page():
    """Demo page — minimal MapAppComponent setup."""
    setup_theme_colors()
    NotificationProvider()

    theme_state = get_current_theme_state()
    notifications = use_notifications()

    # Reactive state — controlled props.
    current_step = solara.use_reactive(None)
    right_panel_open = solara.use_reactive(True)

    def on_step_action(step_id: int, event: str) -> None:
        notifications.success(f"step {step_id} action: {event}")
        if event == "apply":
            current_step.set(None)

    steps = [
        StepConfig(
            id=1,
            name="AOI",
            icon="mdi-map-marker",
            display="step",
            content=AoiStep,
        ),
        StepConfig(
            id=2,
            name="Settings",
            icon="mdi-cog",
            display="dialog",
            content=SettingsDialog,
            actions=(
                StepAction(label="Cancel", event="cancel", cancel=True),
                StepAction(label="Apply", event="apply"),
            ),
        ),
        StepConfig(
            id=3,
            name="Toggle right panel",
            icon="mdi-view-dashboard",
            display="step",
            right_panel_action="toggle",
            content_enabled=False,
        ),
    ]

    panel_config = RightPanelConfig(
        title="Tools",
        icon="mdi-tools",
        width=360,
        description="Active layers and legend.",
    )

    sections = [
        PanelSection(
            title="Layers",
            icon="mdi-layers",
            content=LayerControls,
        ),
        PanelSection(
            title="Legend",
            icon="mdi-format-list-bulleted",
            content=LegendSection,
            divider=True,
        ),
    ]

    external_links = [
        ExternalLink(
            title="pysepal docs",
            url="https://sepal-ui.readthedocs.io/",
            icon="mdi-book-open-page-variant",
        ),
    ]

    # Using `with` lets us drop floating overlay content into the main
    # area without going through a step or panel section.
    with MapAppComponent(
        app_title="MapAppComponent demo",
        app_icon="mdi-earth",
        sepal_map=None,  # supply a SepalMap here when running with GEE
        steps=steps,
        current_step=current_step,
        right_panel_config=panel_config,
        right_panel_content=sections,
        right_panel_open=right_panel_open,
        external_links=external_links,
        theme_state=theme_state,
        on_step_action=on_step_action,
    ):
        # This is rendered in the main map area's children slot.
        solara.Markdown(
            "**Demo mode** — replace `sepal_map=None` with a `SepalMap` "
            "instance to see the embedded map."
        )
