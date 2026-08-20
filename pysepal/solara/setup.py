"""Setup utilities for Solara applications using pysepal.

This module provides utilities to configure common Solara server settings
that are typically needed across all pysepal-based applications.
"""

import logging
from pathlib import Path
from typing import List, Optional, Union

import solara
import solara.server.settings

from .asset_merger import create_merged_assets_directory

logger = logging.getLogger("sepalui.solara.setup")

DEFAULT_FONT_AWESOME = "/@fortawesome/fontawesome-free@6.7.2/css/all.min.css"
DEFAULT_CULL_TIMEOUT = "0s"

# Shared stylesheet consumed by BOTH runtimes; merged into the Solara assets
# ahead of the Solara override sheet. The Voila runtime loads the same file via
# frontend.styles.get_custom_css().
SHARED_BASE_CSS = Path(__file__).parent.parent / "frontend" / "css" / "base.css"


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
    """Configure common Solara server settings for pysepal applications.

    This function sets up standard configurations that are commonly needed
    across pysepal-based Solara applications, avoiding the need to duplicate
    these settings in every application.

    Always includes:
    - FontAwesome 6.7.2
    - pysepal common assets (CSS, JS)
    - No kernel timeout ("0s") (helps to kill sessions once the page is closed)

    If extra asset locations are provided, this function will merge all CSS and JS
    files into combined files to ensure they are all properly served by Solara.

    Args:
        extra_asset_locations: Additional asset locations to serve beyond pysepal's common assets

    """
    logger.debug("Setting up Solara server configuration for sepal_ui application")

    solara.server.settings.assets.fontawesome_path = DEFAULT_FONT_AWESOME
    solara.server.settings.kernel.cull_timeout = DEFAULT_CULL_TIMEOUT

    # Get pysepal common assets
    sepal_common_assets = Path(__file__).parent / "common" / "assets"
    if not sepal_common_assets.exists():
        logger.warning(f"sepal_ui common assets directory not found: {sepal_common_assets}")
        return

    # Always merge so the shared base.css is served alongside the Solara
    # override sheet (and any extra locations). Both the "no extra locations"
    # and "extra locations" cases go through the same path.
    extra_paths = [Path(loc) for loc in (extra_asset_locations or [])]
    if extra_paths:
        logger.debug(f"Extra asset locations: {[str(p) for p in extra_paths]}")

    merged_assets_dir = create_merged_assets_directory(
        sepal_common_assets, extra_paths, base_css_files=[SHARED_BASE_CSS]
    )
    solara.server.settings.assets.extra_locations = [str(merged_assets_dir)]
    logger.debug(f"Asset location set to merged directory: {merged_assets_dir}")

    logger.info("Solara server configuration completed successfully")
