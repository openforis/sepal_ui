"""Utility functions for working with GEE interfaces in Solara applications.

This module provides convenient helper functions to access the current
GEE interface and SepalClient without having to manage sessions manually.
"""

import logging
from typing import Optional

from pysepal_api import SepalClient

from pysepal.scripts.drive_interface import GDriveInterface
from pysepal.scripts.gee_interface import GEEInterface

from .session_manager import SessionManager, empty_session_info

logger = logging.getLogger(__name__)


def get_current_gee_interface() -> GEEInterface:
    """Returns the GEE interface for the current runtime.

    Under an app-launcher Solara server every connection gets its own
    interface, built from that connection's SEPAL headers. A SEPAL sandbox,
    Voila, plain Jupyter and plain scripts share one process-wide interface
    built from the machine's own credentials -- which in those runtimes belong
    to exactly one user.

    Returns:
        The interface for this runtime.

    Raises:
        SepalSessionError: A per-connection runtime has no session, i.e. the
            Page component is missing ``@with_sepal_sessions``.
    """
    return SessionManager().get_gee_interface()


def get_current_sepal_client(module_name: Optional[str] = None) -> Optional[SepalClient]:
    """Returns a SepalClient for the current runtime's session.

    One session holds one client per module name; without ``module_name`` you
    get the client of the route currently rendering (the ``module_name`` of the
    innermost ``@with_sepal_sessions`` entered).

    Args:
        module_name: Return the client for this module instead of the active one.

    Returns:
        The client, or None when there is no session, no such module client, or
        no SEPAL identity for this process (a notebook or script outside a
        SEPAL sandbox, where file I/O goes to the local filesystem).
    """
    return SessionManager().get_sepal_client(module_name=module_name)


def get_current_drive_interface() -> GDriveInterface:
    """Returns the Drive interface for the current runtime.

    Resolved exactly as :func:`get_current_gee_interface`.

    Returns:
        The interface for this runtime.

    Raises:
        SepalSessionError: A per-connection runtime has no session, i.e. the
            Page component is missing ``@with_sepal_sessions``.
    """
    return SessionManager().get_drive_interface()


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
    scope_ids = session_manager.session_scope_ids()
    active_sessions = [session_manager.get_session_info(scope_id) for scope_id in scope_ids]

    return {
        "total_sessions": len(scope_ids),
        "ready_sessions": sum(1 for s in active_sessions if s["session_ready"]),
        "sessions": active_sessions,
    }
