"""Utility functions for working with GEE interfaces in Solara applications.

This module provides convenient helper functions to access the current
GEE interface and SepalClient without having to manage sessions manually.
"""

import logging
from typing import Optional

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


def get_current_session_info() -> dict:
    """Returns session information for the current kernel."""
    session_manager = SessionManager()
    kernel_id = session_manager.get_kernel_id()

    # Get the current session directly
    current_session = session_manager._sessions.get(kernel_id)

    if current_session is None:
        return {
            "kernel_id": kernel_id,
            "username": None,
            "has_gee_interface": False,
            "has_sepal_client": False,
            "session_ready": False,
        }

    return {
        "kernel_id": kernel_id,
        "username": current_session.get("username"),
        "has_gee_interface": current_session.get("gee_interface") is not None,
        "has_sepal_client": current_session.get("sepal_client") is not None,
        "session_ready": current_session.get("gee_interface") is not None,
    }


def get_sessions_overview() -> dict:
    """Returns overview information about all active sessions."""
    session_manager = SessionManager()
    all_sessions = session_manager.list_sessions()

    # Collect statistics about all sessions
    active_sessions = []
    for kernel_id, session in all_sessions.items():
        session_info = {
            "kernel_id": kernel_id,
            "username": session.get("username"),
            "has_gee_interface": session.get("gee_interface") is not None,
            "has_sepal_client": session.get("sepal_client") is not None,
            "session_ready": session.get("gee_interface") is not None,
        }
        active_sessions.append(session_info)

    return {
        "total_sessions": len(all_sessions),
        "ready_sessions": sum(1 for s in active_sessions if s["session_ready"]),
        "sessions": active_sessions,
    }
