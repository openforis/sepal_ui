"""Solara integration utilities for sepal_ui.

This module provides utilities for integrating sepal_ui with Solara applications,
including session management, decorators, and interface utilities.
"""

from .decorators import with_sepal_sessions
from .setup import setup_solara_server, setup_theme_colors
from .utils import (
    get_current_drive_interface,
    get_current_gee_interface,
    get_current_sepal_client,
    get_current_session_info,
    get_sessions_overview,
)

__all__ = [
    "get_current_drive_interface",
    "get_current_gee_interface",
    "get_current_sepal_client",
    "get_current_session_info",
    "get_sessions_overview",
    "setup_solara_server",
    "setup_theme_colors",
    "with_sepal_sessions",
]
