"""Utility functions for working with GEE interfaces in Solara applications.

This module provides convenient helper functions to access the current
GEE interface and SepalClient without having to manage sessions manually.
"""

import logging
from typing import Optional

from eeclient.client import EESession

from sepal_ui.scripts.drive_interface import GDriveInterface
from sepal_ui.scripts.gee_interface import GEEInterface
from sepal_ui.scripts.sepal_client import SepalClient

from .session_manager import SessionManager

logger = logging.getLogger(__name__)

# Module-level fallback instances (created lazily)
_fallback_gee_interface: Optional[GEEInterface] = None
_fallback_drive_interface: Optional[GDriveInterface] = None


def _get_fallback_gee_interface() -> GEEInterface:
    """Get or create the fallback GEE interface with EESession without headers."""
    global _fallback_gee_interface
    if _fallback_gee_interface is None:
        logger.debug("Creating fallback GEEInterface with EESession without headers")
        # if we do not pass headers, the EESession will use the local credentials file
        ee_session = EESession()
        _fallback_gee_interface = GEEInterface(ee_session)
    return _fallback_gee_interface


def _get_fallback_drive_interface() -> GDriveInterface:
    """Get or create the fallback Drive interface without headers."""
    global _fallback_drive_interface
    if _fallback_drive_interface is None:
        logger.debug("Creating fallback GDriveInterface without headers")
        # if we do not pass headers, the interface will use the local credentials file
        _fallback_drive_interface = GDriveInterface()
    return _fallback_drive_interface


def get_current_gee_interface() -> GEEInterface:
    """Returns the GEE interface for the current kernel session.

    If session manager is not initialized, returns a shared fallback GEEInterface
    with an EESession without headers.
    """
    if SessionManager.is_initialized():
        session_manager = SessionManager()
        interface = session_manager.get_session_component("gee_interface")
        if interface is not None:
            return interface

    # Fallback: return shared GEEInterface with EESession without headers
    return _get_fallback_gee_interface()


def get_current_sepal_client() -> Optional[SepalClient]:
    """Returns SepalClient for the current kernel session.

    If session manager is not initialized, returns None since SepalClient
    requires session_id which is only available through session manager.
    """
    if SessionManager.is_initialized():
        session_manager = SessionManager()
        return session_manager.get_session_component("sepal_client")

    logger.debug("Session manager not initialized, SepalClient not available")
    return None


def get_current_drive_interface() -> GDriveInterface:
    """Returns Drive interface for the current kernel session.

    If session manager is not initialized, returns a shared fallback GDriveInterface
    without headers.
    """
    if SessionManager.is_initialized():
        session_manager = SessionManager()
        interface = session_manager.get_session_component("drive_interface")
        if interface is not None:
            return interface

    # Fallback: return shared GDriveInterface without headers
    return _get_fallback_drive_interface()


def get_current_session_info() -> dict:
    """Returns session information for the current kernel.

    Raises:
        RuntimeError: If session manager is not initialized.
    """
    if not SessionManager.is_initialized():
        raise RuntimeError(
            "Session manager is not initialized. "
            "Use @with_sepal_sessions decorator to initialize sessions first."
        )

    session_manager = SessionManager()
    return session_manager.get_session_info()


def get_sessions_overview() -> dict:
    """Returns overview information about all active sessions.

    Raises:
        RuntimeError: If session manager is not initialized.
    """
    if not SessionManager.is_initialized():
        raise RuntimeError(
            "Session manager is not initialized. "
            "Use @with_sepal_sessions decorator to initialize sessions first."
        )

    session_manager = SessionManager()
    all_sessions = session_manager.list_sessions()

    # Collect statistics about all sessions
    active_sessions = []
    for kernel_id in all_sessions.keys():
        session_info = session_manager.get_session_info(kernel_id)
        active_sessions.append(session_info)

    return {
        "total_sessions": len(all_sessions),
        "ready_sessions": sum(1 for s in active_sessions if s["session_ready"]),
        "sessions": active_sessions,
    }
