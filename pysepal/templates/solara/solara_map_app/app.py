"""Solara map application template — `MapAppComponent` reference.

Demonstrates the new Solara-native `MapAppComponent`:

- Typed `StepConfig` / `PanelSection` / `RightPanelConfig` props.
- `with MapAppComponent(...): ...` syntax for floating overlays.
- Lazy step content via `@solara.component` render callables.
- Mixing pre-built ipyvuetify widgets through `embed_widget(...)`.
- Auto-wired `ThemeState` and notification CSS variables.
"""

import logging

import ee
import solara
from component.model import AppModel

import pysepal.sepalwidgets as sw
from pysepal.mapping import SepalMap
from pysepal.scripts.utils import init_ee
from pysepal.solara import (
    MapAppComponent,
    NotificationProvider,
    get_current_drive_interface,
    get_current_gee_interface,
    get_current_sepal_client,
    get_current_theme_state,
    setup_sessions,
    setup_solara_server,
    setup_theme_colors,
    with_sepal_sessions,
)
from pysepal.solara.components.admin import AdminButton
from pysepal.solara.components.layout import (
    PanelSection,
    RightPanelConfig,
    StepConfig,
    embed_widget,
)

logger = logging.getLogger("SEPALUI.map_app")
logger.debug(">>>>>>>>>>> Starting MAP APP example application <<<<<<<<<<")
init_ee()

setup_solara_server()


@solara.lab.on_kernel_start
def on_kernel_start():
    """Set up sessions management for Solara applications."""
    return setup_sessions()


def _ndvi_image():
    """Compute a small NDVI demo image around Bogotá."""
    polygons = ee.FeatureCollection(
        [
            ee.Feature(ee.Geometry.Rectangle([-74.15, 4.77, -74.10, 4.72]), {"name": "Tile A"}),
            ee.Feature(ee.Geometry.Rectangle([-74.09, 4.77, -74.04, 4.72]), {"name": "Tile B"}),
        ]
    )
    s2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(polygons)
        .filterDate("2024-01-01", "2024-12-31")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
        .median()
    )
    return s2.normalizedDifference(["B8", "B4"]).rename("NDVI")


@solara.component
def AoiStep():
    """Solara render fn used for both `step` and `dialog` step displays."""
    with solara.Card(title="Area of Interest Selection"):
        solara.Markdown("Select your area of interest on the map.")
        solara.Button(label="Select AOI", color="primary")


@solara.component
@with_sepal_sessions(module_name="sdg_indicators/15.4.2")
def Page():
    """Main application page — MapAppComponent reference.

    Mounts `NotificationProvider` for toast/task UI and the new
    `MapAppComponent` with two example steps and a right panel.
    """
    setup_theme_colors()
    NotificationProvider()

    gee_interface = get_current_gee_interface()
    get_current_drive_interface()
    get_current_sepal_client()
    theme_state = get_current_theme_state()

    model = AppModel()
    solara_admin = AdminButton(model, logger_instance=logger)

    map_ = SepalMap(gee_interface=gee_interface, fullscreen=True, theme_state=theme_state)
    map_.center = [4.75, -74.12]

    async def _get_maps():
        """Compute the NDVI demo layer."""
        map_.center = [4.75, -74.12]
        map_.zoom = 5
        map_.remove_all()
        await map_.add_ee_layer_async(_ndvi_image())
        map_.zoom = 12

    def remove_all_layers():
        map_.zoom = 5
        map_.center = [4.75, -74.12]
        map_.remove_all()

    btn_compute = sw.TaskButton("add layer", small=True, block=True)
    btn_remove = sw.Btn("remove all layers", small=True, block=True)
    btn_remove.on_event("click", lambda *args: remove_all_layers())

    def create_compute_maps_task():
        return gee_interface.create_task(func=_get_maps, key="compute_all_maps")

    btn_compute.configure(task_factory=create_compute_maps_task)

    steps = [
        StepConfig(
            id=2,
            name="AOI Selection as step",
            icon="mdi-map-marker-check",
            display="step",
            content=AoiStep,
        ),
        StepConfig(
            id=3,
            name="AOI Selection as dialog",
            icon="mdi-map-marker-check",
            display="dialog",
            content=AoiStep,
        ),
        StepConfig(
            id=5,
            name="Toggle sidebar panel",
            icon="mdi-view-dashboard",
            display="step",
            right_panel_action="toggle",
            content_enabled=False,
        ),
    ]

    right_panel_config = RightPanelConfig(
        title="Results",
        icon="mdi-image-filter-hdr",
        width=400,
        description="Visualize and export layers.",
        toggle_icon="mdi-chart-line",
    )

    @solara.component
    def IntroSection():
        solara.Markdown(
            "Select the AOI from one of the steps on the left, then add "
            "the demo NDVI layer below."
        )

    right_panel_content = [
        PanelSection(
            title="Visualize and export layers",
            icon="mdi-layers",
            content=IntroSection,
            description="Add the NDVI layer to the map.",
        ),
        # Pre-built ipyvuetify widgets (admin button + action buttons)
        # are wrapped via `embed_widget` so they slot into a typed section.
        PanelSection(
            title="Tools",
            icon="mdi-tools",
            content=embed_widget(solara_admin, btn_remove, btn_compute),
            divider=True,
        ),
    ]

    MapAppComponent(
        app_title="My test App",
        app_icon="mdi-image-filter-hdr",
        sepal_map=map_,
        steps=steps,
        right_panel_config=right_panel_config,
        right_panel_content=right_panel_content,
        right_panel_open=True,
        theme_state=theme_state,
        dialog_width=750,
    )
