"""Session-scoped theme state and Solara hooks."""

from __future__ import annotations

from typing import Optional

import solara
from traitlets import Bool, Enum, HasTraits

from pysepal.frontend.styles import get_theme


class ThemeState(HasTraits):
    """Session-scoped theme preference and resolved dark/light state."""

    mode = Enum(values=["dark", "light", "auto"], default_value="auto")
    dark = Bool(False)

    def __init__(self, mode: str = "auto", dark: Optional[bool] = None, **kwargs):
        """Initialize with an initial mode and optional explicit dark value."""
        super().__init__(**kwargs)
        self.set_mode(mode)
        if dark is not None:
            self.set_dark(dark)

    def set_mode(self, mode: str) -> None:
        """Update theme preference and keep fixed modes aligned with `dark`."""
        self.mode = mode
        if mode == "dark":
            self.dark = True
        elif mode == "light":
            self.dark = False

    def set_dark(self, dark: bool) -> None:
        """Update the effective dark/light value."""
        self.dark = bool(dark)

    @staticmethod
    def mode_to_widget_dark(mode: str) -> Optional[bool]:
        """Map theme mode to ThemeToggle.dark semantics."""
        if mode == "auto":
            return None
        return mode == "dark"

    @staticmethod
    def widget_dark_to_mode(value: Optional[bool]) -> str:
        """Map ThemeToggle.dark semantics back to theme mode."""
        if value is None:
            return "auto"
        return "dark" if value else "light"


_fallback_theme_state: Optional[ThemeState] = None


def _get_fallback_theme_state() -> ThemeState:
    """Get or create a process-local fallback theme state."""
    global _fallback_theme_state
    if _fallback_theme_state is None:
        fallback_mode = get_theme()
        _fallback_theme_state = ThemeState(mode=fallback_mode, dark=fallback_mode == "dark")
    return _fallback_theme_state


def get_current_theme_state() -> ThemeState:
    """Return the theme state for the current Solara kernel session."""
    from .session_manager import SessionManager, can_create_sessions

    if SessionManager.is_initialized():
        session_manager = SessionManager()
        theme_state = session_manager.get_session_component("theme_state")
        if theme_state is not None:
            return theme_state

        if not can_create_sessions():
            return _get_fallback_theme_state()

        raise RuntimeError(
            "Session manager is active but no theme state exists for the current kernel. "
            "Ensure your Page component is decorated with @with_sepal_sessions."
        )

    return _get_fallback_theme_state()


def resolve_theme_state(theme_state: Optional[ThemeState] = None) -> ThemeState:
    """Return a usable ThemeState without ever raising.

    Precedence: an explicit ``theme_state`` > the current session's theme state
    > a process-local fallback. Unlike :func:`get_current_theme_state`, an active
    session that is missing its theme component degrades to the fallback instead
    of raising, so callers such as ``NotificationProvider`` cannot crash a
    misconfigured app.
    """
    if theme_state is not None:
        return theme_state
    try:
        return get_current_theme_state()
    except RuntimeError:
        return _get_fallback_theme_state()


def use_theme_dark(theme_state: Optional[ThemeState] = None) -> bool:
    """Reactively return the effective dark/light state for the current session."""
    theme_state = theme_state or get_current_theme_state()
    dark, set_dark = solara.use_state(bool(theme_state.dark))

    def _observe():
        def handler(change):
            set_dark(bool(change["new"]))

        theme_state.observe(handler, "dark")
        return lambda: theme_state.unobserve(handler, "dark")

    solara.use_effect(_observe, [id(theme_state)])
    return dark
