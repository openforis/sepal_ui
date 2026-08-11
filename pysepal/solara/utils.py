"""Utility functions for working with GEE interfaces in Solara applications.

This module provides convenient helper functions to access the current
GEE interface and SepalClient without having to manage sessions manually.
"""

import logging
from typing import Optional

from eeclient.client import EESession
from pysepal_api import SepalClient

from pysepal.scripts.drive_interface import GDriveInterface
from pysepal.scripts.gee_interface import GEEInterface

from .session_manager import SessionManager, can_create_sessions, empty_session_info

logger = logging.getLogger(__name__)

# Module-level fallback instances (created lazily)
_fallback_gee_interface: Optional[GEEInterface] = None
_fallback_drive_interface: Optional[GDriveInterface] = None


def _get_fallback_gee_interface() -> GEEInterface:
    """Get or create the fallback GEE interface with EESession without headers."""
    global _fallback_gee_interface
    if _fallback_gee_interface is None:
        logger.debug("Creating fallback GEEInterface with EESession.from_default()")
        # from_default() resolves local credentials (the SEPAL file in a SEPAL
        # context, otherwise EARTHENGINE_TOKEN / the Earth Engine OAuth file).
        # A bare EESession() raises under ee-client 3.0.0 (agnostic auth).
        ee_session = EESession.from_default()
        _fallback_gee_interface = GEEInterface(ee_session)
    return _fallback_gee_interface


def _get_fallback_drive_interface() -> GDriveInterface:
    """Get or create the fallback Drive interface without headers."""
    global _fallback_drive_interface
    if _fallback_drive_interface is None:
        logger.debug("Creating fallback GDriveInterface without headers")
        # headerless GDriveInterface resolves local credentials via
        # eeclient.providers.resolve_default_provider() (see GDriveInterface).
        _fallback_drive_interface = GDriveInterface()
    return _fallback_drive_interface


def get_current_gee_interface() -> GEEInterface:
    """Returns the GEE interface for the current kernel session.

    If session manager is not initialized (e.g. running in a notebook),
    returns a shared fallback GEEInterface with an EESession without headers.

    Raises:
        RuntimeError: If session manager is initialized but no session exists
            for the current kernel (indicates a missing @with_sepal_sessions decorator).
    """
    if SessionManager.is_initialized():
        session_manager = SessionManager()
        interface = session_manager.get_session_component("gee_interface")
        if interface is not None:
            return interface

        if not can_create_sessions():
            logger.debug("No SEPAL session is possible here; using the fallback")
            return _get_fallback_gee_interface()

        raise RuntimeError(
            "Session manager is active but no session exists for the current kernel. "
            "Ensure your Page component is decorated with @with_sepal_sessions."
        )

    # Fallback only for non-Solara contexts (notebooks, scripts)
    return _get_fallback_gee_interface()


def get_current_sepal_client(module_name: Optional[str] = None) -> Optional[SepalClient]:
    """Returns a SepalClient for the current runtime scope's session.

    One session holds one client per module name; without ``module_name`` you
    get the client of the route currently rendering (the ``module_name`` of the
    innermost ``@with_sepal_sessions`` entered).

    Args:
        module_name: Return the client for this module instead of the active one.

    Returns:
        The client, or None when no session manager or session exists.
    """
    if not SessionManager.is_initialized():
        logger.debug("Session manager not initialized, SepalClient not available")
        return None

    return SessionManager().get_sepal_client(module_name=module_name)


def get_current_drive_interface() -> GDriveInterface:
    """Returns Drive interface for the current kernel session.

    If session manager is not initialized (e.g. running in a notebook),
    returns a shared fallback GDriveInterface without headers.

    Raises:
        RuntimeError: If session manager is initialized but no session exists
            for the current kernel (indicates a missing @with_sepal_sessions decorator).
    """
    if SessionManager.is_initialized():
        session_manager = SessionManager()
        interface = session_manager.get_session_component("drive_interface")
        if interface is not None:
            return interface

        if not can_create_sessions():
            logger.debug("No SEPAL session is possible here; using the fallback")
            return _get_fallback_drive_interface()

        raise RuntimeError(
            "Session manager is active but no session exists for the current kernel. "
            "Ensure your Page component is decorated with @with_sepal_sessions."
        )

    # Fallback only for non-Solara contexts (notebooks, scripts)
    return _get_fallback_drive_interface()


def get_current_session_info() -> dict:
    """Returns session information for the current runtime scope.

    Never raises. An uninitialised session manager, an unresolvable runtime and
    a scope with no session all report the same "not ready" shape, so admin and
    debug UI render under Solara, Voila and plain Jupyter alike. Deliberately
    does not instantiate ``SessionManager``: constructing it would flip
    ``is_initialized()`` on for the whole process as a side effect.
    """
    if not SessionManager.is_initialized():
        logger.debug("Session manager not initialized; reporting an empty session")
        return empty_session_info(None)

    return SessionManager().get_session_info()


def get_sessions_overview() -> dict:
    """Returns overview information about all active sessions.

    Never raises; see :func:`get_current_session_info`.
    """
    if not SessionManager.is_initialized():
        return {"total_sessions": 0, "ready_sessions": 0, "sessions": []}

    session_manager = SessionManager()
    all_sessions = session_manager.list_sessions()
    active_sessions = [session_manager.get_session_info(k) for k in all_sessions]

    return {
        "total_sessions": len(all_sessions),
        "ready_sessions": sum(1 for s in active_sessions if s["session_ready"]),
        "sessions": active_sessions,
    }
