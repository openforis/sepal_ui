"""Setup utilities for Solara applications using sepal_ui.

This module provides utilities to configure common Solara server settings
that are typically needed across all sepal_ui-based applications.
"""

import logging
from pathlib import Path
from typing import List, Optional, Union

import solara
import solara.server.settings

logger = logging.getLogger("sepalui.solara.setup")

DEFAULT_FONT_AWESOME = "/@fortawesome/fontawesome-free@6.7.2/css/all.min.css"
DEFAULT_CULL_TIMEOUT = "0s"


def setup_theme_colors():
    """Configure default sepalui theme colors for the application."""
    # Dark theme colors
    solara.lab.theme.themes.dark.primary = "#76591e"
    solara.lab.theme.themes.dark.primary_contrast = "#bf8f2d"
    solara.lab.theme.themes.dark.secondary = "#363e4f"
    solara.lab.theme.themes.dark.secondary_contrast = "#5d76ab"
    solara.lab.theme.themes.dark.error = "#a63228"
    solara.lab.theme.themes.dark.info = "#c5c6c9"
    solara.lab.theme.themes.dark.success = "#3f802a"
    solara.lab.theme.themes.dark.warning = "#b8721d"
    solara.lab.theme.themes.dark.accent = "#272727"
    solara.lab.theme.themes.dark.anchor = "#f3f3f3"
    solara.lab.theme.themes.dark.main = "#24221f"
    solara.lab.theme.themes.dark.darker = "#1a1a1a"
    solara.lab.theme.themes.dark.bg = "#121212"
    solara.lab.theme.themes.dark.menu = "#424242"

    # Light theme colors
    solara.lab.theme.themes.light.primary = "#5BB624"
    solara.lab.theme.themes.light.primary_contrast = "#76b353"
    solara.lab.theme.themes.light.accent = "#f3f3f3"
    solara.lab.theme.themes.light.anchor = "#f3f3f3"
    solara.lab.theme.themes.light.secondary = "#2199C4"
    solara.lab.theme.themes.light.secondary_contrast = "#5d76ab"
    solara.lab.theme.themes.light.main = "#2196f3"
    solara.lab.theme.themes.light.darker = "#ffffff"
    solara.lab.theme.themes.light.bg = "#FFFFFF"
    solara.lab.theme.themes.light.menu = "#FFFFFF"


def setup_solara_server(
    extra_asset_locations: Optional[List[Union[str, Path]]] = None,
) -> None:
    """Configure common Solara server settings for sepal_ui applications.

    This function sets up standard configurations that are commonly needed
    across sepal_ui-based Solara applications, avoiding the need to duplicate
    these settings in every application.

    Always includes:
    - FontAwesome 6.7.2
    - sepal_ui common assets (CSS, JS)
    - No kernel timeout ("0s") (helps to kill sessions once the page is closed)

    Args:
        extra_asset_locations: Additional asset locations to serve beyond sepal_ui's common assets

    """
    logger.debug("Setting up Solara server configuration for sepal_ui application")

    solara.server.settings.assets.fontawesome_path = DEFAULT_FONT_AWESOME
    solara.server.settings.kernel.cull_timeout = DEFAULT_CULL_TIMEOUT
    # Configure asset locations

    asset_locations = []

    # Always include sepal_ui's common assets
    sepal_common_assets = Path(__file__).parent / "common" / "assets"
    if sepal_common_assets.exists():
        asset_locations.append(str(sepal_common_assets))
        logger.debug(f"Added sepal_ui common assets: {sepal_common_assets}")
    else:
        logger.warning(f"sepal_ui common assets directory not found: {sepal_common_assets}")

    # Add user-specified extra asset locations
    if extra_asset_locations:
        for location in extra_asset_locations:
            asset_locations.append(str(location))
            logger.debug(f"Added extra asset location: {location}")

    # Set the asset locations (only if we have any)
    if asset_locations:
        solara.server.settings.assets.extra_locations = asset_locations
        logger.debug(f"Total asset locations configured: {len(asset_locations)}")

    logger.info("Solara server configuration completed successfully")
