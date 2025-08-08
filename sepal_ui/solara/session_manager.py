"""Session Manager for gee, drive and sepal interfaces for Solara applications.

This module provides centralized session management for gee, gdrive and sepal interfaces,
handling initialization, cleanup, and session tracking across different
Solara applications.
"""

import logging
import os
from typing import Any, Callable, Dict, Optional

import solara
import solara.server.kernel_context
from eeclient.client import EESession
from eeclient.helpers import get_sepal_headers_from_auth
from eeclient.models import SepalHeaders
from solara.lab import headers

from sepal_ui.scripts.drive_interface import GDriveInterface
from sepal_ui.scripts.gee_interface import GEEInterface
from sepal_ui.scripts.sepal_client import SepalClient

logger = logging.getLogger("sepalui.session_manager")


class SessionManager:
    """A singleton session manager for solara-sepal applications.

    This class manages the lifecycle of sessions across different Solara applications,
    providing a centralized way to handle session creation, retrieval, and cleanup for
    GEE interfaces, SepalClient and GDriveInterface.
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

    def get_kernel_id(self) -> str:
        """Get the current kernel ID."""
        # Solara provides a way to get the current kernel context
        return id(solara.server.kernel_context.get_current_context().kernel)

    def create_session(self, module_name: str = "default") -> None:
        """Create a new session with all the interfaces for the given kernel ID.

        Args:
            kernel_id: The kernel ID to create session for. If None, uses current kernel.
            module_name: The module name for the SepalClient.

        Raises:
            EEClientError: For authentication-related errors.
            Exception: For other validation or connection errors.
        """
        current_headers = headers.value
        kernel_id = self.get_kernel_id()

        if current_headers is None:
            logger.warning(f"Headers not available yet for kernel {kernel_id}")
            return

        logger.debug(f"Creating session for kernel {kernel_id}")

        sepal_headers = (
            get_sepal_headers_from_auth()
            if os.getenv("SOLARA_TEST", "false").lower() == "true"
            else SepalHeaders.model_validate(current_headers)
        )

        username = sepal_headers.sepal_user.username

        sepal_session_id = sepal_headers.cookies["SEPAL-SESSIONID"]
        gee_session = EESession(sepal_headers=sepal_headers)

        gee_interface = GEEInterface(gee_session)
        sepal_client = SepalClient(session_id=sepal_session_id, module_name=module_name)
        drive_interface = GDriveInterface(sepal_headers=sepal_headers)

        self._sessions[kernel_id] = {
            "username": username,
            "gee_interface": gee_interface,
            "sepal_client": sepal_client,
            "drive_interface": drive_interface,
        }
        logger.debug(
            f"Sessions created for kernel {kernel_id} and gee_interface {id(gee_interface)}"
        )

    def get_current_sepal_client(self, kernel_id: Optional[str] = None) -> Optional[SepalClient]:
        """Get the SepalClient for the current kernel session.

        Args:
            kernel_id: The kernel ID to get client for. If None, uses current kernel.

        Returns:
            SepalClient instance or None if session not available.
        """
        return self.get_session_component("sepal_client", kernel_id)

    def cleanup_session(self, kernel_id: str) -> None:
        """Clean up a session for the given kernel ID.

        Args:
            kernel_id: The kernel ID to clean up.
        """
        logger.debug(f"Cleaning up session for kernel {kernel_id}")

        if kernel_id in self._sessions:
            session = self._sessions[kernel_id]
            try:
                session["gee_interface"].close()
            except Exception as e:
                logger.error(f"Error closing GEE interface for kernel {kernel_id}: {e}")

            del self._sessions[kernel_id]
            logger.debug(f"Session cleaned up for kernel {kernel_id}")

    def get_current_gee_interface(self, kernel_id: Optional[str] = None) -> Optional[GEEInterface]:
        """Get the GEE interface for the current kernel session.

        Args:
            kernel_id: The kernel ID to get interface for. If None, uses current kernel.

        Returns:
            GEEInterface instance or None if session not available.
        """
        return self.get_session_component("gee_interface", kernel_id)

    def get_current_drive_interface(
        self, kernel_id: Optional[str] = None
    ) -> Optional[GDriveInterface]:
        """Get the Drive interface for the current kernel session.

        Args:
            kernel_id: The kernel ID to get interface for. If None, uses current kernel.

        Returns:
            GDriveInterface instance or None if session not available.
        """
        return self.get_session_component("drive_interface", kernel_id)

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

        return session.get(component_name)

    def list_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active sessions."""
        return self._sessions.copy()


def setup_sessions() -> Callable:
    """Set up sessions management for Solara applications.

    This function should be called with the @solara.lab.on_kernel_start decorator
    to automatically manage GEE, Drive, and Sepal sessions for your application.

    Returns:
        Cleanup function to be called when kernel shuts down.
    """
    session_manager = SessionManager()
    kernel_id = session_manager.get_kernel_id()

    logger.debug(f"Setting up sepal sessions for kernel {kernel_id}")

    # Return cleanup function
    def cleanup():
        session_manager.cleanup_session(kernel_id)

    return cleanup
