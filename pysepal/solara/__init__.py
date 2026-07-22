"""Solara integration utilities for sepal_ui.

This module provides utilities for integrating sepal_ui with Solara applications,
including session management, decorators, and interface utilities.
"""

from .decorators import with_sepal_sessions
from .locale import (
    LocaleState,
    get_current_locale_state,
    match_offered_locale,
    resolve_locale_state,
    use_locale,
)
from .notifications import (
    NotificationProvider,
    notify,
    track_task,
    use_notifications,
)
from .session_manager import setup_sessions
from .setup import setup_solara_server, setup_theme_colors
from .theme import ThemeState, get_current_theme_state, use_theme_dark
from .utils import (
    get_current_drive_interface,
    get_current_gee_interface,
    get_current_sepal_client,
    get_current_session_info,
    get_sessions_overview,
)

__all__ = [
    "LocaleState",
    "NotificationProvider",
    "ThemeState",
    "get_current_drive_interface",
    "get_current_gee_interface",
    "get_current_locale_state",
    "get_current_sepal_client",
    "get_current_session_info",
    "get_current_theme_state",
    "get_sessions_overview",
    "match_offered_locale",
    "notify",
    "resolve_locale_state",
    "setup_sessions",
    "setup_solara_server",
    "setup_theme_colors",
    "track_task",
    "use_locale",
    "use_theme_dark",
    "use_notifications",
    "with_sepal_sessions",
]
