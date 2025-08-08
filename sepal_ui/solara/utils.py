"""Utility functions for working with GEE interfaces in Solara applications.

This module provides convenient helper functions to access the current
GEE interface and SepalClient without having to manage sessions manually.
"""

import logging
from typing import Optional

import solara

from sepal_ui.scripts.drive_interface import GDriveInterface
from sepal_ui.scripts.gee_interface import GEEInterface
from sepal_ui.scripts.sepal_client import SepalClient

from .session_manager import SessionManager

logger = logging.getLogger(__name__)


def get_current_gee_interface() -> Optional[GEEInterface]:
    """Returns the GEE interface for the current kernel session."""
    session_manager = SessionManager()
    return session_manager.get_current_gee_interface()


def get_current_sepal_client() -> Optional[SepalClient]:
    """Returns SepalClient for the current kernel session."""
    session_manager = SessionManager()
    return session_manager.get_current_sepal_client()


def get_current_drive_interface() -> Optional[GDriveInterface]:
    """Returns Drive interface for the current kernel session."""
    session_manager = SessionManager()
    return session_manager.get_current_drive_interface()


def get_session_info() -> dict:
    """Returns session information for the current kernel."""
    session_manager = SessionManager()
    kernel_id = session_manager.get_kernel_id()
    gee_interface = session_manager.get_current_gee_interface()
    sepal_client = session_manager.get_current_sepal_client()

    return {
        "kernel_id": kernel_id,
        "has_gee_interface": gee_interface is not None,
        "has_sepal_client": sepal_client is not None,
        "session_ready": gee_interface is not None,
        "total_sessions": len(session_manager.list_sessions()),
    }


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
