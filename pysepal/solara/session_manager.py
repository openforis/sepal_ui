"""Session Manager for gee, drive and sepal interfaces for Solara applications.

This module provides centralized session management for gee, gdrive and sepal interfaces,
handling initialization, cleanup, and session tracking across different
Solara applications.
"""

import logging
import os
import threading
from collections import deque
from typing import Any, Callable, Deque, Dict, Optional

from eeclient.client import EESession
from eeclient.helpers import get_sepal_headers_from_auth
from eeclient.models import SepalHeaders
from pysepal_api import SepalClient
from solara.lab import headers

from pysepal.scripts.drive_interface import GDriveInterface
from pysepal.scripts.gee_interface import GEEInterface
from pysepal.solara.errors import (
    MissingSepalHeadersError,
    SepalSessionError,
    SessionScopeClosedError,
)
from pysepal.solara.runtime_context import (
    UnsupportedSolaraRuntimeError,
    get_current_runtime_id,
)
from pysepal.solara.ui_state import clear_scoped_state, has_scoped_state

logger = logging.getLogger("sepalui.session_manager")

__all__ = [
    "MissingSepalHeadersError",
    "SepalSessionError",
    "SessionManager",
    "SessionScopeClosedError",
    "can_create_sessions",
    "empty_session_info",
    "reset_dev_headers_cache",
    "resolve_sepal_headers",
    "setup_sessions",
]

CLOSED_SCOPE_MEMORY = 256
"How many cleaned-up scope ids to remember, to refuse late resurrection."

_dev_headers: Optional[SepalHeaders] = None
_dev_headers_lock = threading.Lock()


def _dev_auth_enabled() -> bool:
    """Whether the deprecated ``SOLARA_TEST`` local-development login is on."""
    return os.getenv("SOLARA_TEST", "false").strip().lower() == "true"


def resolve_sepal_headers(raw_headers: dict) -> SepalHeaders:
    """Validate a connection's raw headers into SEPAL headers.

    Under ``SOLARA_TEST=true`` the headers come from a real SEPAL login
    instead, cached for the process: ``get_sepal_headers_from_auth`` issues a
    blocking HTTP POST and ``create_session`` runs on the render path.

    Args:
        raw_headers: The request headers Solara exposes for this connection.

    Returns:
        The validated SEPAL headers.
    """
    global _dev_headers

    if not _dev_auth_enabled():
        return SepalHeaders.model_validate(raw_headers)

    with _dev_headers_lock:
        if _dev_headers is None:
            _dev_headers = get_sepal_headers_from_auth()
        return _dev_headers


def reset_dev_headers_cache() -> None:
    """Drop the cached development headers (tests, and dev-server reloads)."""
    global _dev_headers

    with _dev_headers_lock:
        _dev_headers = None


def empty_session_info(kernel_id: Optional[str]) -> dict:
    """Return the canonical "no session exists here" payload.

    Args:
        kernel_id: The scope the caller asked about, or None when no scope
            could be resolved at all (script, pytest, unsupported kernel).

    Returns:
        A session-info dict with every capability flag off.
    """
    return {
        "kernel_id": kernel_id,
        "username": None,
        "has_gee_interface": False,
        "has_sepal_client": False,
        "has_drive_interface": False,
        "has_theme_state": kernel_id is not None and has_scoped_state("theme_state", kernel_id),
        "active_module_name": None,
        "module_names": [],
        "session_ready": False,
    }


class SessionManager:
    """A singleton session manager for solara-sepal applications.

    This class manages the lifecycle of sessions across different Solara applications,
    providing a centralized way to handle session creation, retrieval, and cleanup for
    GEE interfaces, SepalClient and GDriveInterface.

    Note: Do not instantiate this class directly. Use the @with_sepal_sessions
    decorator or the utility functions in sepal_ui.solara.utils instead.
    """

    _instance = None
    """Singleton instance of the SessionManager."""
    _sessions: Dict[str, Dict[str, Any]] = {}
    """Dictionary to hold sessions keyed by kernel ID."""

    def __new__(cls):
        """Create or return the singleton instance of SessionManager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the SessionManager singleton instance."""
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._sessions = {}
            self._registry_lock = threading.Lock()
            self._scope_locks: Dict[str, threading.Lock] = {}
            self._closed_scopes: Deque[str] = deque(maxlen=CLOSED_SCOPE_MEMORY)

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if the SessionManager has been initialized."""
        return cls._instance is not None and hasattr(cls._instance, "_initialized")

    def get_kernel_id(self) -> str:
        """Get the current supported Solara/Voila runtime ID."""
        return get_current_runtime_id()

    def _scope_lock(self, kernel_id: str) -> threading.Lock:
        """Return the lock guarding one scope's session.

        Per scope on purpose: session construction performs blocking network
        calls, so a single global lock would serialise every user's first
        render in a multi-user container.

        Never popped from ``_scope_locks`` on cleanup: a thread that fetched
        this lock but has not yet acquired it could otherwise end up holding
        an orphaned lock while a new one is handed out for the same
        ``kernel_id``, letting two threads into the critical section at once.
        The leaked ``Lock`` objects are negligible next to the session leak
        that not calling cleanup at all would already cause.
        """
        with self._registry_lock:
            return self._scope_locks.setdefault(kernel_id, threading.Lock())

    def _reopen_scope(self, kernel_id: str) -> None:
        """Forget a scope's tombstone because its kernel is genuinely restarting.

        Solara's hot-reload restarts a kernel in place: it runs the on-close
        callbacks (our ``cleanup_session``, which tombstones the scope) and
        then re-runs ``on_kernel_start`` -- i.e. ``setup_sessions`` -- for the
        *same* kernel id. Without this, the tombstone would permanently brick
        that scope on the very first file save. Only ``setup_sessions`` calls
        this, so a late callback on another thread can't trigger it.

        Takes the scope lock, not just the registry lock: ``cleanup_session``
        writes the tombstone from inside its own scope-lock section, well
        after ``_close_session`` (which can block for seconds closing the GEE
        interface). Without the scope lock here, a reopen landing while that
        close is still in flight would find no tombstone to remove yet, and
        then lose the race when cleanup writes one moments later -- bricking
        the scope for good, exactly what this method exists to prevent.

        Args:
            kernel_id: The scope whose kernel is (re)starting.
        """
        with self._scope_lock(kernel_id):
            with self._registry_lock:
                while kernel_id in self._closed_scopes:
                    self._closed_scopes.remove(kernel_id)

    def create_session(self, module_name: str = "default") -> None:
        """Create -- or reuse -- the session for the current runtime scope.

        Runs on every render of a ``@with_sepal_sessions`` component, so the
        common case is the raw-header fast path: the same connection hands back
        the same headers object and nothing is parsed. Otherwise the headers are
        validated and the session is idempotent per *identity* rather than per
        scope -- a session whose username or SEPAL-SESSIONID no longer matches
        is torn down and rebuilt, because a bare scope-id check would hand a
        recycled scope the previous user's interfaces. On an already-live session,
        a ``SepalClient.create()`` failure for a new ``module_name`` propagates
        as-is and leaves the session -- and its other modules' clients -- intact.

        Args:
            module_name: The module name for the SepalClient.

        Raises:
            MissingSepalHeadersError: The runtime carries no SEPAL headers.
            SessionScopeClosedError: The scope was already cleaned up.
            EEClientError: For authentication-related errors.
        """
        kernel_id = self.get_kernel_id()

        current_headers = headers.value
        if current_headers is None:
            raise MissingSepalHeadersError(
                f"No SEPAL authentication headers are available for scope {kernel_id}; "
                "a SEPAL session cannot be created without them."
            )

        with self._scope_lock(kernel_id):
            with self._registry_lock:
                if kernel_id in self._closed_scopes:
                    raise SessionScopeClosedError(
                        f"Scope {kernel_id} was cleaned up; refusing to resurrect its session."
                    )

            existing = self._sessions.get(kernel_id)
            if existing is not None and existing.get("raw_headers") is current_headers:
                logger.debug(f"Reusing session for scope {kernel_id}")
                self._ensure_sepal_client(existing, module_name)
                return

            sepal_headers = resolve_sepal_headers(current_headers)
            username = sepal_headers.sepal_user.username
            sepal_session_id = sepal_headers.cookies["SEPAL-SESSIONID"]

            if existing is not None:
                if (
                    existing.get("username") == username
                    and existing.get("sepal_session_id") == sepal_session_id
                ):
                    existing["raw_headers"] = current_headers
                    logger.debug(f"Reusing session for scope {kernel_id}")
                    self._ensure_sepal_client(existing, module_name)
                    return

                logger.warning(
                    f"Identity changed on scope {kernel_id} "
                    f"({existing.get('username')} -> {username}); rebuilding the session"
                )
                # Unlink before closing: GEEInterface() below is unguarded, and a
                # scope must never expose a session whose interfaces are already closed.
                self._sessions.pop(kernel_id, None)
                self._close_session(kernel_id, existing)

            logger.debug(f"Creating session for scope {kernel_id}")
            gee_session = EESession.from_sepal_headers(sepal_headers)
            gee_interface = GEEInterface(gee_session)
            session: Dict[str, Any] = {
                "username": username,
                "sepal_session_id": sepal_session_id,
                "raw_headers": current_headers,
                "gee_interface": gee_interface,
                "sepal_clients": {},
                "active_module_name": module_name,
                "drive_interface": None,
            }
            try:
                self._ensure_sepal_client(session, module_name)
                session["drive_interface"] = GDriveInterface(sepal_headers=sepal_headers)
            except BaseException:
                # Close whatever was actually built before re-raising -- otherwise a
                # flapping SEPAL API leaks one GEEInterface (and its event loop) per render.
                self._close_session(kernel_id, session)
                raise

            self._sessions[kernel_id] = session

        logger.debug(
            f"Sessions created for kernel {kernel_id} and gee_interface {id(gee_interface)}"
        )

    def _ensure_sepal_client(self, session: Dict[str, Any], module_name: str) -> SepalClient:
        """Return the session's client for ``module_name``, creating it on miss.

        One session per scope holds one client per module name. Keying whole
        sessions by (scope, module) would multiply ``GEEInterface``, and each of
        those owns a private event loop.

        Args:
            session: The session payload to read and mutate.
            module_name: The module whose client is required.

        Returns:
            The client for ``module_name``, which also becomes the active one.
        """
        clients = session["sepal_clients"]
        client = clients.get(module_name)
        if client is None:
            client = SepalClient.create(
                session_id=session["sepal_session_id"], module_name=module_name
            )
            clients[module_name] = client
            logger.debug(f"Created SepalClient for module '{module_name}'")

        # Deliberately after creation succeeds: if SepalClient.create() raises above,
        # this line never runs and the active module keeps pointing at a route that
        # actually has a client, instead of one whose client failed to build.
        session["active_module_name"] = module_name
        return client

    def get_sepal_client(
        self, module_name: Optional[str] = None, kernel_id: Optional[str] = None
    ) -> Optional[SepalClient]:
        """Get a SepalClient held by a scope's session.

        Args:
            module_name: The module whose client to return. Defaults to the
                module of the most recently entered ``@with_sepal_sessions``
                component, i.e. the route being rendered.
            kernel_id: The scope to read from. If None, uses the current one.

        Returns:
            The client, or None when no session or no such module client exists.
        """
        if kernel_id is None:
            try:
                kernel_id = self.get_kernel_id()
            except UnsupportedSolaraRuntimeError:
                # Deliberately swallowed here but not in get_session_component: this is
                # get_current_sepal_client()'s documented "returns None" contract (PR body),
                # not a promise get_current_gee_interface()/_drive_interface() also make.
                return None

        session = self._sessions.get(kernel_id)
        if session is None:
            return None

        name = module_name or session.get("active_module_name")
        return session.get("sepal_clients", {}).get(name)

    def cleanup_session(self, kernel_id: str) -> None:
        """Close and forget the session for a scope, then tombstone the scope.

        The tombstone is permanent until ``_reopen_scope`` lifts it -- which
        only happens when ``setup_sessions`` runs again for this same
        ``kernel_id``, i.e. a genuine kernel restart, not a reconnect.

        Args:
            kernel_id: The scope to clean up.
        """
        logger.debug(f"Cleaning up session for kernel {kernel_id}")

        with self._scope_lock(kernel_id):
            session = self._sessions.pop(kernel_id, None)
            if session is not None:
                self._close_session(kernel_id, session)
            with self._registry_lock:
                if kernel_id not in self._closed_scopes:
                    self._closed_scopes.append(kernel_id)

        logger.debug(f"Session cleaned up for kernel {kernel_id}")

    def _close_session(self, kernel_id: str, session: Dict[str, Any]) -> None:
        """Release a session's interfaces. Does not touch the registry.

        Args:
            kernel_id: The scope the session belonged to, for logging.
            session: The session payload to close.
        """
        gee_interface = session.get("gee_interface")
        if gee_interface is not None:
            try:
                gee_interface.close()
            except Exception as e:
                logger.error(f"Error closing GEE interface for kernel {kernel_id}: {e}")

        for module_name, client in session.get("sepal_clients", {}).items():
            try:
                client.close()
            except Exception as e:
                logger.error(
                    f"Error closing SepalClient '{module_name}' for kernel {kernel_id}: {e}"
                )

        # GDriveInterface only grows close() in ee-client 4.0.0; skip it below that.
        close_drive = getattr(session.get("drive_interface"), "close", None)
        if close_drive is not None:
            try:
                close_drive()
            except Exception as e:
                logger.error(f"Error closing Drive interface for kernel {kernel_id}: {e}")

    def get_session_component(
        self, component_name: str, kernel_id: Optional[str] = None
    ) -> Optional[Any]:
        """Get a specific component from a session.

        Args:
            component_name: The name/key of the component to retrieve.
            kernel_id: The kernel ID to get component from. If None, uses current kernel.

        Returns:
            The component instance or None if not found.
        """
        if kernel_id is None:
            kernel_id = self.get_kernel_id()

        if kernel_id not in self._sessions:
            return None

        session = self._sessions[kernel_id]
        username = session.get("username", "unknown")

        # debug log for session retrieval
        logger.debug(
            f"Retrieving component '{component_name}' for kernel {kernel_id}, user {username}"
        )

        if component_name == "sepal_client":
            return self.get_sepal_client(kernel_id=kernel_id)

        return session.get(component_name)

    def get_session_info(self, kernel_id: Optional[str] = None) -> dict:
        """Get session information for a specific scope.

        Never raises: a runtime with no resolvable scope reports a None
        ``kernel_id`` and a not-ready session, so UI can render anywhere.

        Args:
            kernel_id: The scope to get info for. If None, uses the current one.

        Returns:
            Dictionary with session information.
        """
        if kernel_id is None:
            try:
                kernel_id = self.get_kernel_id()
            except UnsupportedSolaraRuntimeError:
                logger.debug("No resolvable runtime scope; reporting an empty session")
                return empty_session_info(None)

        current_session = self._sessions.get(kernel_id)

        if current_session is None:
            return empty_session_info(kernel_id)

        return {
            "kernel_id": kernel_id,
            "username": current_session.get("username"),
            "has_gee_interface": current_session.get("gee_interface") is not None,
            "has_sepal_client": bool(current_session.get("sepal_clients")),
            "has_drive_interface": current_session.get("drive_interface") is not None,
            "has_theme_state": has_scoped_state("theme_state", kernel_id),
            "active_module_name": current_session.get("active_module_name"),
            "module_names": sorted(current_session.get("sepal_clients", {})),
            "session_ready": current_session.get("gee_interface") is not None,
        }

    def list_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active sessions."""
        return self._sessions.copy()


def can_create_sessions() -> bool:
    """Whether a SEPAL session can exist for the current runtime at all.

    ``create_session`` needs solara's request headers. Voila, plain Jupyter and
    plain scripts never have them, so a missing session there is expected rather
    than a forgotten ``@with_sepal_sessions`` -- callers should degrade to their
    headerless fallback instead of raising.
    """
    return headers.value is not None


def setup_sessions() -> Callable:
    """Set up sessions management for Solara applications.

    This function should be called with the @solara.lab.on_kernel_start decorator
    to automatically manage GEE, Drive, and Sepal sessions for your application.
    Also lifts this kernel's tombstone, if any: solara's hot-reload restarts a
    kernel in place, re-running ``on_kernel_start`` for the same kernel id right
    after the close callbacks tombstoned it.

    Returns:
        Cleanup function to be called when kernel shuts down.
    """
    session_manager = SessionManager()
    kernel_id = session_manager.get_kernel_id()
    session_manager._reopen_scope(kernel_id)

    logger.debug(f"Setting up sepal sessions for kernel {kernel_id}")

    # Return cleanup function
    def cleanup():
        session_manager.cleanup_session(kernel_id)
        clear_scoped_state(kernel_id)

    return cleanup
