"""Solara map application template for SEPAL UI.

This module provides a complete example of a map-based application built with Solara
and SEPAL UI components, including AOI selection, map visualization, and admin tools.
"""
import logging

import solara
from component.model import AppModel
from solara.lab.components.theming import theme

from sepal_ui.aoi import AoiView
from sepal_ui.mapping import SepalMap
from sepal_ui.scripts.utils import init_ee
from sepal_ui.sepalwidgets.vue_app import MapApp, ThemeToggle
from sepal_ui.solara import (
    get_current_drive_interface,
    get_current_gee_interface,
    get_current_sepal_client,
    get_current_session_info,
    setup_sessions,
    setup_solara_server,
    setup_theme_colors,
    with_sepal_sessions,
)
from sepal_ui.solara.components.admin import AdminButton

logger = logging.getLogger("map_app")
logger.debug(">>>>>>>>>>> Starting MAP APP example application <<<<<<<<<<")
init_ee()

# Setup Solara server configuration (mandatory settings + optional extra assets)
setup_solara_server()  # or setup_solara_server(extra_asset_locations=["./my_assets/"])


@solara.lab.on_kernel_start
def init_gee():
    """Initialize Google Earth Engine and setup sessions on kernel start.

    Returns:
        The result of setup_sessions() call.
    """
    return setup_sessions()


@solara.component
@with_sepal_sessions(module_name="sdg_indicators/15.4.2")
def Page():
    """Main page component for the map application.

    Creates and renders the complete map application interface including
    theme controls, map widget, AOI selection, and admin tools.
    """
    setup_theme_colors()
    theme_toggle = ThemeToggle()
    theme_toggle.observe(lambda e: setattr(theme, "dark", e["new"]), "dark")

    gee_interface = get_current_gee_interface()
    get_current_drive_interface()
    get_current_sepal_client()
    username = get_current_session_info()["username"]

    # Just a model to store the app name
    model = AppModel()

    solara_admin = AdminButton(
        username,
        model,
        logger_instance=logger,
    )

    # Main map widget
    map_ = SepalMap(gee_interface=gee_interface, fullscreen=True, theme_toggle=theme_toggle)
    aoi_view = AoiView(
        gee_interface=gee_interface,
        map_=map_,
    )

    some_widget = solara.Text("This is a placeholder for the main content of the map application.")

    steps_data = [
        {
            "id": 2,
            "name": "AOI Selection",
            "icon": "mdi-map-marker-check",
            "display": "dialog",
            "content": aoi_view,
        },
        {
            "id": 2,
            "name": "Sidebar panel",
            "icon": "mdi-view-dashboard",
            "display": "dialog",
            "content": [],
            "right_panel_action": "toggle",  # "open", "close", "toggle", or None
        },
    ]

    # This is for the secondary panel
    extra_content_config = {
        "title": "Results",
        "icon": "mdi-image-filter-hdr",
        "width": 400,
        "description": "Some description.",
        "toggle_icon": "mdi-chart-line",
    }

    extra_content_data = [
        {
            "title": "Visualize and export layers",
            "icon": "mdi-layers",
            "content": [some_widget],
            "description": "To add layers to the map, you will first need to select the area of interest and the years in the 3. Indicator settings step.",
        },
    ]

    if username == "admin":
        extra_content_data.append(
            {
                "title": "Admin",
                "icon": "mdi-shield-account",
                "content": [solara_admin],
                "description": "Admin tools for development and troubleshooting.",
            }
        )

    MapApp.element(
        app_title="My test App",
        app_icon="mdi-image-filter-hdr",
        main_map=[map_],
        steps_data=steps_data,
        extra_content_config=extra_content_config,
        extra_content_data=extra_content_data,
        theme_toggle=[theme_toggle],
        dialog_width=750,
    )
