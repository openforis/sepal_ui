"""Runtime topology: where a session's credentials may legitimately come from.

A session's credential source is decided by *runtime topology* -- what kind of
process pysepal is running in -- and never by probing credentials or by testing
whether a request happens to carry headers. The rule, in order:

1. ``PYSEPAL_DEV_AUTH`` is armed and the connection carries no validated SEPAL
   headers: :attr:`SessionSource.DEV_AUTH`, one developer login for the whole
   process. Real headers demote this branch, so a stray environment variable can
   never displace a live user's identity.
2. The process runs in a SEPAL sandbox -- ``SEPAL=true`` in the environment,
   i.e. an app-manager app owned by exactly one user:
   :attr:`SessionSource.PROCESS`.
3. The process runs under a Solara server -- an app-launcher multi-user
   container: :attr:`SessionSource.PER_CONNECTION`.
4. Anything else -- Voila, plain Jupyter, a script, pytest:
   :attr:`SessionSource.PROCESS`.

:attr:`SessionSource.PER_CONNECTION` never falls back. An app-launcher container
mounts the *platform* GEE service-account key at
``~/.config/earthengine/credentials`` (``ee.Initialize()`` requires it there),
and that is exactly the path ``eeclient.providers.resolve_default_provider``
reads -- so a headerless fallback in that runtime silently hands every user the
platform service account.

This rule governs the session layer, not the whole package.
``pysepal.scripts.gee.init_ee`` reads ``~/.config/earthengine/credentials``
directly, branches on ``type == "service_account"`` and calls
``ee.Initialize()``; a ``GEEInterface`` built with no session then routes every
call through that global ``ee``. Two public defaults still reach it --
``solara.components.aoi.admin.process_admin(..., gee=True)`` with no
``gee_interface``, and ``SepalMap(gee=True)`` likewise -- so in an app-launcher
container both use the platform service account rather than the caller's
identity. pysepal's own render paths pass ``get_current_gee_interface()``, so
nothing here regresses; the gap is in the public API and predates this rule.

These names are private on purpose: exporting the enum in a major release
freezes its members, and this is the enum most likely to gain a case.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Mapping

import solara

if not hasattr(solara, "_using_solara_server"):
    raise ImportError(
        "solara._using_solara_server is missing. Rule 3 above reads it to tell "
        "an app-launcher container from any other runtime; without it every "
        "session creation fails at render time instead of here. Install a "
        "solara that provides it (pysepal pins solara>=1.60,<2)."
    )

DEV_AUTH_ENV_VAR = "PYSEPAL_DEV_AUTH"
"Environment variable arming the local-development login."

SEPAL_ENV_VAR = "SEPAL"
"Environment variable the SEPAL sandbox image exports as ``true``."

_TRUTHY = frozenset({"1", "true", "yes", "on"})


class SessionSource(Enum):
    """Where a session's credentials come from."""

    PROCESS = "process"
    """One session for the whole process, from the machine's own credentials."""

    PER_CONNECTION = "per_connection"
    """One session per connection, from that connection's SEPAL headers."""

    DEV_AUTH = "dev_auth"
    """One session for the whole process, from a developer login."""


@dataclass(frozen=True)
class SessionPlan:
    """A credential source together with the rule that selected it."""

    source: SessionSource
    reason: str


def is_sepal_sandbox(env: Mapping[str, str]) -> bool:
    """Whether this process runs in a SEPAL sandbox, which exports ``SEPAL=true``.

    The two failure directions are not symmetric: a false positive here steers
    a multi-user container onto PROCESS and silently shares one identity across
    every user, while a false negative only steers a real sandbox onto
    PER_CONNECTION, which raises loudly on missing headers. A safety core must
    fail toward loud.

    That asymmetry is why this reads the environment rather than the home
    directory name. Only the sandbox image sets ``SEPAL`` -- the
    geospatial-toolkit build writes it into ``/etc/environment``, and its
    ``sandbox-base`` parent does not -- so an app-launcher app container built
    on ``sandbox-base`` inherits a ``sepal-user`` home but no ``SEPAL``. Under
    the home-name predicate that container was a false positive.

    Only the exact value ``true`` counts, matching
    :func:`pysepal.scripts.scratch.on_sepal`, the other reader of this
    variable. That is stricter than :func:`dev_auth_enabled` on purpose:
    ``PYSEPAL_DEV_AUTH`` is typed by a developer, ``SEPAL`` is written by the
    platform.

    ``eeclient.providers._is_sepal_context()`` still matches ``"sepal-user"``
    against the home directory name, and gates ``resolve_default_provider()``'s
    fail-closed SEPAL-file-only branch. The two predicates now read different
    signals and disagree in exactly the container above, where ee-client keeps
    the old false positive; moving it onto ``SEPAL`` is a separate release.

    Args:
        env: The environment to read, normally ``os.environ``.

    Returns:
        True in a SEPAL sandbox, where the machine credentials belong to the
        one user who owns the sandbox.
    """
    return env.get(SEPAL_ENV_VAR, "").strip().lower() == "true"


def dev_auth_enabled(env: Mapping[str, str]) -> bool:
    """Whether ``PYSEPAL_DEV_AUTH`` is armed.

    Args:
        env: The environment to read, normally ``os.environ``.

    Returns:
        True when the variable is ``1``, ``true``, ``yes`` or ``on``.
    """
    return env.get(DEV_AUTH_ENV_VAR, "").strip().lower() in _TRUTHY


def resolve_session_plan(
    *,
    env: Mapping[str, str],
    using_solara_server: bool,
    has_sepal_headers: bool,
) -> SessionPlan:
    """Decide the credential source from runtime topology alone.

    Pure: every input is injected, so the combinations CI cannot stage -- a real
    sandbox, a real app-launcher container -- stay table-testable.

    Args:
        env: The process environment. Read by rules 1 and 2.
        using_solara_server: Whether a Solara server is running this process.
        has_sepal_headers: Whether the connection carries *validated* SEPAL
            headers. Read by rule 1 only, as the interlock that stops a
            developer login from displacing a real user. It never selects
            between PROCESS and PER_CONNECTION.

    Returns:
        The plan, carrying the rule that chose it.
    """
    if dev_auth_enabled(env) and not has_sepal_headers:
        return SessionPlan(SessionSource.DEV_AUTH, f"{DEV_AUTH_ENV_VAR} is armed")

    if is_sepal_sandbox(env):
        return SessionPlan(SessionSource.PROCESS, f"SEPAL sandbox ({SEPAL_ENV_VAR} is true)")

    if using_solara_server:
        return SessionPlan(SessionSource.PER_CONNECTION, "running under a Solara server")

    return SessionPlan(SessionSource.PROCESS, "no Solara server and no SEPAL sandbox")


def current_session_plan(*, has_sepal_headers: bool) -> SessionPlan:
    """Resolve the plan for the running process.

    Args:
        has_sepal_headers: See :func:`resolve_session_plan`. Callers may pass
            False without validating anything whenever :func:`dev_auth_enabled`
            is False, because rule 1 is the only reader.

    Returns:
        The plan for this runtime.
    """
    return resolve_session_plan(
        env=os.environ,
        using_solara_server=solara._using_solara_server(),
        has_sepal_headers=has_sepal_headers,
    )
