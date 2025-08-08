"""Solara integration utilities for sepal_ui.

This module provides utilities for integrating sepal_ui with Solara applications,
including session management, decorators, and interface utilities.
"""

from .decorators import with_sepal_sessions
from .session_manager import setup_sessions
from .utils import (
    get_current_drive_interface,
    get_current_gee_interface,
    get_current_sepal_client,
    get_session_info,
    setup_theme_colors,
)

__all__ = [
    "with_sepal_sessions",
    "setup_sessions",
    "get_current_drive_interface",
    "get_current_gee_interface",
    "get_current_sepal_client",
    "get_session_info",
    "setup_theme_colors",
]
