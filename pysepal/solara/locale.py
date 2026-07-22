"""Session-scoped locale state and Solara hooks.

Mirrors ``pysepal.solara.theme``: the ``LocaleSelect`` widget resolves the
effective locale in the browser (localStorage -> legacy config seed ->
``navigator.language`` -> "en") and pushes only the *resolved* code into the
session's ``LocaleState``. Python never resolves locale itself, and the
process-local fallback is a constant "en" that NEVER reads
``~/.sepal-ui-config`` — code running outside a session (pytest, scripts)
is therefore deterministic regardless of the machine's config file.
"""

from __future__ import annotations

from typing import Iterable, Optional

import solara
from traitlets import HasTraits, Unicode


def match_offered_locale(candidate: str, offered: Iterable[str]) -> str:
    """Return the code from ``offered`` that best matches ``candidate``.

    Order: exact match, bare primary subtag if offered, first offered variant
    sharing the primary subtag (in ``offered`` order). Returns ``""`` when
    nothing matches so callers can fall through to their next source.
    """
    if not candidate:
        return ""
    offered = list(offered)
    if candidate in offered:
        return candidate
    primary = candidate.split("-")[0]
    if primary in offered:
        return primary
    return next((code for code in offered if code.split("-")[0] == primary), "")


class LocaleState(HasTraits):
    """Session-scoped resolved locale (IETF BCP 47 code offered by the app)."""

    locale = Unicode("en")

    def __init__(self, locale: str = "en", **kwargs):
        """Initialize with an initial resolved locale code."""
        super().__init__(**kwargs)
        self.set_locale(locale)

    def set_locale(self, locale: str) -> None:
        """Update the resolved locale; empty values coerce to "en"."""
        self.locale = locale or "en"


_fallback_locale_state: Optional[LocaleState] = None


def _get_fallback_locale_state() -> LocaleState:
    """Get or create the process-local fallback locale state.

    Deliberately a constant "en" with no config read — see module docstring.
    """
    global _fallback_locale_state
    if _fallback_locale_state is None:
        _fallback_locale_state = LocaleState("en")
    return _fallback_locale_state


def get_current_locale_state() -> LocaleState:
    """Return the locale state for the current Solara kernel session."""
    from .session_manager import SessionManager

    if SessionManager.is_initialized():
        session_manager = SessionManager()
        locale_state = session_manager.get_session_component("locale_state")
        if locale_state is not None:
            return locale_state

        raise RuntimeError(
            "Session manager is active but no locale state exists for the current kernel. "
            "Ensure your Page component is decorated with @with_sepal_sessions."
        )

    return _get_fallback_locale_state()


def resolve_locale_state(locale_state: Optional[LocaleState] = None) -> LocaleState:
    """Return a usable LocaleState without ever raising.

    Precedence: an explicit ``locale_state`` > the current session's locale
    state > the constant-"en" process fallback.
    """
    if locale_state is not None:
        return locale_state
    try:
        return get_current_locale_state()
    except RuntimeError:
        return _get_fallback_locale_state()


def use_locale(locale_state: Optional[LocaleState] = None) -> str:
    """Reactively return the resolved locale code for the current session."""
    locale_state = locale_state or resolve_locale_state()
    locale, set_locale = solara.use_state(locale_state.locale)

    def _observe():
        def handler(change):
            set_locale(change["new"])

        locale_state.observe(handler, "locale")
        return lambda: locale_state.unobserve(handler, "locale")

    solara.use_effect(_observe, [id(locale_state)])
    return locale
