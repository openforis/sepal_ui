"""Read-only session-status payloads.

``get_session_info`` used to hand back a plain dict that mixed a UI-scope fact
(``has_theme_state``) into an authentication payload, and ``list_sessions``
returned a shallow copy of the private session registry, so public callers held
live references they could mutate. These are frozen value objects: what admin
and debug UI may read, and nothing more.
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class SessionInfo:
    """One runtime scope's SEPAL session status.

    ``scope_id`` is always populated: it is a runtime fact, resolvable whether
    or not a session, or even a ``SessionManager``, exists.
    """

    scope_id: str
    username: Optional[str] = None
    has_gee_interface: bool = False
    has_sepal_client: bool = False
    has_drive_interface: bool = False
    active_module_name: Optional[str] = None
    module_names: Tuple[str, ...] = ()
    session_ready: bool = False


@dataclass(frozen=True)
class SessionsOverview:
    """Every session the process currently holds."""

    sessions: Tuple[SessionInfo, ...] = ()

    @property
    def total_sessions(self) -> int:
        """How many scopes hold a session."""
        return len(self.sessions)

    @property
    def ready_sessions(self) -> int:
        """How many of those sessions have a live GEE interface."""
        return sum(1 for session in self.sessions if session.session_ready)
