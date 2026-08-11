"""Errors raised while establishing a SEPAL session.

One hierarchy, one module: ``session_manager`` imports and re-exports these
names, so ``except MissingSepalHeadersError`` works whether the caller got the
name from here or from ``session_manager``.
"""


class SepalSessionError(RuntimeError):
    """Base error for SEPAL session creation problems."""


class MissingSepalHeadersError(SepalSessionError):
    """Raised when the current runtime carries no SEPAL authentication headers."""


class SessionScopeClosedError(SepalSessionError):
    """Raised when a session is requested for a scope that was already cleaned up."""
