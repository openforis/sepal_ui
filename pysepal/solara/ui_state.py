"""Scope-keyed UI state for pysepal Solara and Voila apps.

UI preferences (theme today, locale next) are per-connection state with no
authentication in their resolution path: a Voila page, a plain notebook or a
script must be able to hold a theme without a SEPAL session existing. This
registry keys that state by
:func:`pysepal.solara.runtime_context.current_scope_id` and falls back to
a single process-wide scope when no runtime can be resolved, so every getter
built on it is total.
"""

import logging
import threading
from typing import Any, Callable, Dict, Optional, TypeVar

from pysepal.solara.runtime_context import PROCESS_SCOPE, current_scope_id

logger = logging.getLogger("sepalui.solara.ui_state")

__all__ = [
    "PROCESS_SCOPE",
    "clear_scoped_state",
    "current_scope_id",
    "get_scoped_state",
    "has_scoped_state",
]

T = TypeVar("T")

_states: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()


def get_scoped_state(name: str, factory: Callable[[], T], scope_id: Optional[str] = None) -> T:
    """Return the ``name`` state for a scope, creating it on miss.

    Args:
        name: Key of the state within the scope, e.g. ``"theme_state"``.
        factory: Zero-argument callable building the state on first access.
        scope_id: Scope to read from; defaults to :func:`current_scope_id`.

    Returns:
        The stored state instance.
    """
    scope = current_scope_id() if scope_id is None else scope_id
    with _lock:
        scope_states = _states.setdefault(scope, {})
        if name not in scope_states:
            scope_states[name] = factory()
            logger.debug(f"Created UI state '{name}' for scope {scope}")
        return scope_states[name]


def has_scoped_state(name: str, scope_id: Optional[str] = None) -> bool:
    """Whether ``name`` already exists for a scope, without creating it.

    Args:
        name: Key of the state within the scope.
        scope_id: Scope to inspect; defaults to :func:`current_scope_id`.

    Returns:
        True when the state exists.
    """
    scope = current_scope_id() if scope_id is None else scope_id
    with _lock:
        return name in _states.get(scope, {})


def clear_scoped_state(scope_id: Optional[str] = None) -> None:
    """Drop every UI state held for a scope.

    Args:
        scope_id: Scope to clear; defaults to :func:`current_scope_id`.
    """
    scope = current_scope_id() if scope_id is None else scope_id
    with _lock:
        removed = _states.pop(scope, None)
    if removed is not None:
        logger.debug(f"Cleared UI state for scope {scope}")
