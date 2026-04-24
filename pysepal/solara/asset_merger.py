"""Asset merging utilities for Solara applications.

This module handles the merging of CSS and JS files from multiple locations
to work around Solara's limitation of serving assets from a single location.
"""

import logging
import shutil
import tempfile
from pathlib import Path
from typing import List

logger = logging.getLogger("sepalui.solara.asset_merger")


def merge_asset_files(sepal_assets_dir: Path, extra_locations: List[Path], temp_dir: Path) -> None:
    """Merge CSS and JS files from sepal_ui and extra locations into combined files.

    Args:
        sepal_assets_dir: Path to sepal_ui common assets
        extra_locations: List of extra asset directory paths
        temp_dir: Temporary directory to create merged files in
    """
    # Merge CSS files
    css_content = []
    js_content = []

    # Start with sepal_ui common assets
    sepal_css = sepal_assets_dir / "custom.css"
    sepal_js = sepal_assets_dir / "custom.js"

    if sepal_css.exists():
        css_content.append(f"/* === sepal_ui common CSS === */\n{sepal_css.read_text()}\n")
        logger.debug(f"Added sepal_ui CSS: {sepal_css}")
    else:
        logger.warning(f"sepal_ui common CSS not found: {sepal_css}")

    if sepal_js.exists():
        js_content.append(f"/* === sepal_ui common JS === */\n{sepal_js.read_text()}\n")
        logger.debug(f"Added sepal_ui JS: {sepal_js}")
    else:
        logger.warning(f"sepal_ui common JS not found: {sepal_js}")

    # Add extra location assets
    for location in extra_locations:
        location_path = Path(location)
        if not location_path.exists():
            logger.warning(f"Extra asset location does not exist: {location_path}")
            continue

        # Look for CSS files
        for css_file in location_path.glob("**/*.css"):
            css_content.append(
                f"/* === {css_file.relative_to(location_path)} === */\n{css_file.read_text()}\n"
            )
            logger.debug(f"Added CSS from {location}: {css_file}")

        # Look for JS files
        for js_file in location_path.glob("**/*.js"):
            js_content.append(
                f"/* === {js_file.relative_to(location_path)} === */\n{js_file.read_text()}\n"
            )
            logger.debug(f"Added JS from {location}: {js_file}")

    # Create merged assets directory structure
    merged_assets_dir = temp_dir / "assets"
    merged_assets_dir.mkdir(exist_ok=True)

    # Write merged files
    if css_content:
        merged_css = merged_assets_dir / "custom.css"
        merged_css.write_text("\n".join(css_content))
        logger.debug(f"Created merged CSS file: {merged_css}")

    if js_content:
        merged_js = merged_assets_dir / "custom.js"
        merged_js.write_text("\n".join(js_content))
        logger.debug(f"Created merged JS file: {merged_js}")

    # Copy any other files from sepal_ui common assets
    if sepal_assets_dir.exists():
        for file_path in sepal_assets_dir.iterdir():
            if file_path.suffix not in [".css", ".js"]:  # Skip CSS/JS as they're merged
                target_file = merged_assets_dir / file_path.name
                shutil.copy2(file_path, target_file)
                logger.debug(f"Copied additional asset: {file_path.name}")


def create_merged_assets_directory(sepal_assets_dir: Path, extra_locations: List[Path]) -> Path:
    """Create a temporary directory with merged assets from all locations.

    Args:
        sepal_assets_dir: Path to sepal_ui common assets
        extra_locations: List of extra asset directory paths

    Returns:
        Path to the directory containing the merged assets (ready for Solara)
    """
    # Create temporary directory for merged assets
    temp_dir = Path(tempfile.mkdtemp(prefix="sepal_ui_assets_"))
    logger.debug(f"Created temporary assets directory: {temp_dir}")

    # Merge all assets
    merge_asset_files(sepal_assets_dir, extra_locations, temp_dir)

    # Return the assets subdirectory (where the actual files are)
    merged_assets_dir = temp_dir / "assets"
    logger.debug(f"Merged assets available at: {merged_assets_dir}")
    return merged_assets_dir
