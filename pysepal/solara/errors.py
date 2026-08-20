"""Errors raised while establishing a SEPAL session.

Defined here, and only here. ``session_manager`` imports
``MissingSepalHeadersError`` and ``SessionScopeClosedError`` in order to raise
them, but its ``__all__`` does not advertise them -- import from
``pysepal.solara.errors``.
"""


class SepalSessionError(RuntimeError):
    """Base error for SEPAL session creation problems."""


class MissingSepalHeadersError(SepalSessionError):
    """Raised when the current runtime carries no SEPAL authentication headers."""


class SessionScopeClosedError(SepalSessionError):
    """Raised when a session is requested for a scope that was already cleaned up."""
