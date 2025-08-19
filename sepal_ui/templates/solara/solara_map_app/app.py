"""Solara map application template for SEPAL UI.

This module provides a complete example of a map-based application built with Solara
and SEPAL UI components, including AOI selection, map visualization, and admin tools.
"""

import logging

import ipyvuetify as v
import solara
from component.model import AppModel
from solara.lab.components.theming import theme

from sepal_ui.mapping import SepalMap
from sepal_ui.scripts.utils import init_ee
from sepal_ui.sepalwidgets.vue_app import MapApp, ThemeToggle
from sepal_ui.solara import (
    get_current_drive_interface,
    get_current_gee_interface,
    get_current_sepal_client,
    setup_sessions,
    setup_solara_server,
    setup_theme_colors,
    with_sepal_sessions,
)
from sepal_ui.solara.components.admin import AdminButton

logger = logging.getLogger("SEPALUI.map_app")
logger.debug(">>>>>>>>>>> Starting MAP APP example application <<<<<<<<<<")
init_ee()

setup_solara_server()  # or setup_solara_server(extra_asset_locations=["./my_assets/"])


@solara.lab.on_kernel_start
def on_kernel_start():
    """Set up sessions management for Solara applications."""
    return setup_sessions()


@solara.component
@with_sepal_sessions(module_name="sdg_indicators/15.4.2")
def Page():
    """Main application page component for the Solara map application.

    This component sets up the main user interface including theme configuration,
    map visualization, AOI selection tools, and administrative features.
    The page is configured with SEPAL sessions for SDG indicators module 15.4.2.
    """
    setup_theme_colors()
    theme_toggle = ThemeToggle()
    theme_toggle.observe(lambda e: setattr(theme, "dark", e["new"]), "dark")

    gee_interface = get_current_gee_interface()
    get_current_drive_interface()
    get_current_sepal_client()

    # Just a model to store the app name
    model = AppModel()

    solara_admin = AdminButton(
        model,
        logger_instance=logger,
    )

    # Main map widget
    map_ = SepalMap(gee_interface=gee_interface, fullscreen=True, theme_toggle=theme_toggle)

    aoi_view = v.Card(
        children=[
            v.CardTitle(children=["Area of Interest Selection"]),
            v.CardText(children=["Select your area of interest on the map."]),
            v.Btn(children=["Select AOI"], color="primary"),
        ]
    )

    steps_data = [
        {
            "id": 2,
            "name": "AOI Selection",
            "icon": "mdi-map-marker-check",
            "display": "step",
            "content": aoi_view,
        },
        {
            "id": 3,
            "name": "AOI Selection",
            "icon": "mdi-map-marker-check",
            "display": "dialog",
            "content": aoi_view,
        },
        {
            "id": 4,
            "name": "Map View",
            "icon": "mdi-map",
            "display": "step",
            "content": map_,
        },
        {
            "id": 5,
            "name": "Sidebar panel",
            "icon": "mdi-view-dashboard",
            "display": "step",
            "content": [],
            "right_panel_action": "toggle",  # "open", "close", "toggle", or None
        },
    ]

    # This is for the secondary panel
    right_panel_config = {
        "title": "Results",
        "icon": "mdi-image-filter-hdr",
        "width": 400,
        "description": "Some description.",
        "toggle_icon": "mdi-chart-line",
    }

    # We can use solara components here!
    right_panel_content_with_solara = [
        {
            "title": "Visualize and export layers",
            "icon": "mdi-layers",
            "content": [solara.Text("This is a Solara component.")],
            "description": "To add layers to the map, you will first need to select the area of interest and the years in the 3. Indicator settings step.",
        },
        {
            "content": [solara_admin],
        },
    ]

    MapApp.element(
        app_title="My test App",
        app_icon="mdi-image-filter-hdr",
        main_map=[map_],
        steps_data=steps_data,
        right_panel_config=right_panel_config,
        right_panel_content=right_panel_content_with_solara,
        right_panel_open=True,
        theme_toggle=[theme_toggle],
        dialog_width=750,
    )
