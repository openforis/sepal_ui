"""Tests for the runtime-topology rules deciding a session's credential source."""

import sys
from pathlib import Path

import pytest

from pysepal.solara._topology import (
    DEV_AUTH_ENV_VAR,
    LOCAL_EE_ENV_VAR,
    SEPAL_ENV_VAR,
    SessionSource,
    current_session_plan,
    dev_auth_enabled,
    is_sepal_sandbox,
    local_ee_enabled,
    plan_reads_sepal_headers,
    resolve_session_plan,
)

SANDBOX = {SEPAL_ENV_VAR: "true"}
"""The environment a SEPAL sandbox image exports."""


def _plan(**overrides):
    kwargs = {
        "env": {},
        "using_solara_server": False,
        "has_sepal_headers": False,
    }
    kwargs.update(overrides)
    return resolve_session_plan(**kwargs)


@pytest.mark.parametrize(
    ("env", "using_solara_server", "has_sepal_headers", "expected"),
    [
        # app-manager app: the sandbox's own credentials are the user's own
        (SANDBOX, False, False, SessionSource.PROCESS),
        (SANDBOX, True, False, SessionSource.PROCESS),
        (SANDBOX, True, True, SessionSource.PROCESS),
        # app-launcher container: one identity per connection, never shared
        ({}, True, False, SessionSource.PER_CONNECTION),
        ({}, True, True, SessionSource.PER_CONNECTION),
        # voila, plain jupyter, a script, pytest
        ({}, False, False, SessionSource.PROCESS),
        # headers alone never select PER_CONNECTION -- only dev-auth reads them
        ({}, False, True, SessionSource.PROCESS),
        # dev auth arms a single process-wide login...
        ({DEV_AUTH_ENV_VAR: "1"}, True, False, SessionSource.DEV_AUTH),
        ({DEV_AUTH_ENV_VAR: "true"}, False, False, SessionSource.DEV_AUTH),
        ({DEV_AUTH_ENV_VAR: "1", **SANDBOX}, False, False, SessionSource.DEV_AUTH),
        # ...but real SEPAL headers always demote it
        ({DEV_AUTH_ENV_VAR: "1"}, True, True, SessionSource.PER_CONNECTION),
        # a disarmed value is not an arming value
        ({DEV_AUTH_ENV_VAR: "false"}, True, False, SessionSource.PER_CONNECTION),
        ({DEV_AUTH_ENV_VAR: ""}, True, False, SessionSource.PER_CONNECTION),
        # local EE lets a GEE-only app run under `solara run` with no SEPAL login
        ({LOCAL_EE_ENV_VAR: "1"}, True, False, SessionSource.PROCESS),
        ({LOCAL_EE_ENV_VAR: "on"}, False, False, SessionSource.PROCESS),
        # ...under the same interlock as dev auth: real headers demote it
        ({LOCAL_EE_ENV_VAR: "1"}, True, True, SessionSource.PER_CONNECTION),
        # a disarmed value leaves the container rule untouched
        ({LOCAL_EE_ENV_VAR: "false"}, True, False, SessionSource.PER_CONNECTION),
        ({LOCAL_EE_ENV_VAR: ""}, True, False, SessionSource.PER_CONNECTION),
        # dev auth outranks it: a SEPAL login is the more specific request
        ({DEV_AUTH_ENV_VAR: "1", LOCAL_EE_ENV_VAR: "1"}, True, False, SessionSource.DEV_AUTH),
    ],
)
def test_topology_table(env, using_solara_server, has_sepal_headers, expected):
    plan = resolve_session_plan(
        env=env,
        using_solara_server=using_solara_server,
        has_sepal_headers=has_sepal_headers,
    )

    assert plan.source is expected
    assert plan.reason


def test_a_multi_user_container_never_degrades_to_process_credentials():
    """R2: PER_CONNECTION is the source that must never fall back.

    An app-launcher container mounts the *platform* GEE service-account key at
    ~/.config/earthengine/credentials -- ee.Initialize() needs it there -- and
    that is the same path resolve_default_provider() reads. A headerless
    fallback there collapses every user onto one identity.
    """
    assert _plan(using_solara_server=True).source is SessionSource.PER_CONNECTION
    assert _plan(using_solara_server=True, has_sepal_headers=True).source is (
        SessionSource.PER_CONNECTION
    )


def test_the_sandbox_rule_wins_over_the_solara_server_rule():
    """An app-manager app runs solara inside the user's own sandbox."""
    assert _plan(env=SANDBOX, using_solara_server=True).source is SessionSource.PROCESS


def test_a_sepal_user_home_alone_is_not_a_sandbox(monkeypatch):
    """The regression this predicate exists for: app-launcher app containers.

    app-launcher builds each app's image from that app's own Dockerfile, and an
    app derived from ``openforis/sandbox-base`` inherits a ``sepal-user`` home
    while ``SEPAL`` stays unset -- only the sandbox image exports it. Reading
    the home name resolved such a container to PROCESS, silently sharing one
    platform identity across every user of the app. Staging a real
    ``sepal-user`` home keeps this red for any predicate that reads it again.
    """
    monkeypatch.setenv("HOME", "/home/sepal-user")
    assert Path.home().name == "sepal-user"

    assert is_sepal_sandbox({}) is False
    assert _plan(using_solara_server=True).source is SessionSource.PER_CONNECTION


@pytest.mark.parametrize(
    ("env", "using_solara_server", "has_sepal_headers", "reason_substring"),
    [
        ({DEV_AUTH_ENV_VAR: "1"}, False, False, DEV_AUTH_ENV_VAR),
        (SANDBOX, False, False, "sandbox"),
        ({LOCAL_EE_ENV_VAR: "1"}, True, False, LOCAL_EE_ENV_VAR),
        # both give PROCESS, so only the reason can show which rule answered
        ({LOCAL_EE_ENV_VAR: "1", **SANDBOX}, True, False, "sandbox"),
        ({}, True, False, "Solara server"),
        ({}, False, False, "no Solara server"),
    ],
)
def test_the_reason_names_the_rule_that_fired(
    env, using_solara_server, has_sepal_headers, reason_substring
):
    """A truthy ``reason`` isn't enough -- it must name the rule that actually fired."""
    plan = resolve_session_plan(
        env=env,
        using_solara_server=using_solara_server,
        has_sepal_headers=has_sepal_headers,
    )

    assert reason_substring in plan.reason


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        (" true ", True),
        ("", False),
        ("false", False),
        ("1", False),
        ("yes", False),
        ("on", False),
    ],
)
def test_is_sepal_sandbox(value, expected):
    """The platform writes ``SEPAL`` as exactly ``true``, so only that counts.

    Deliberately stricter than ``PYSEPAL_DEV_AUTH`` below, which accepts
    1/true/yes/on because a developer types it by hand: the two are not meant
    to agree. This matches ``pysepal.scripts.scratch.on_sepal``, the other
    reader of the same variable.
    """
    assert is_sepal_sandbox({SEPAL_ENV_VAR: value}) is expected


def test_is_sepal_sandbox_is_false_when_the_variable_is_absent():
    assert is_sepal_sandbox({}) is False


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1", True),
        ("true", True),
        ("TRUE", True),
        ("yes", True),
        ("on", True),
        ("0", False),
        ("false", False),
        ("", False),
        ("maybe", False),
    ],
)
def test_dev_auth_enabled(value, expected):
    assert dev_auth_enabled({DEV_AUTH_ENV_VAR: value}) is expected


def test_dev_auth_disabled_when_the_variable_is_absent():
    assert dev_auth_enabled({}) is False


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1", True),
        ("true", True),
        ("TRUE", True),
        ("yes", True),
        ("on", True),
        ("0", False),
        ("false", False),
        ("", False),
        ("maybe", False),
    ],
)
def test_local_ee_enabled(value, expected):
    """Typed by a developer, so it accepts the same spellings as dev auth."""
    assert local_ee_enabled({LOCAL_EE_ENV_VAR: value}) is expected


def test_local_ee_disabled_when_the_variable_is_absent():
    assert local_ee_enabled({}) is False


@pytest.mark.parametrize(
    ("env", "expected"),
    [
        ({}, False),
        ({DEV_AUTH_ENV_VAR: "1"}, True),
        ({LOCAL_EE_ENV_VAR: "1"}, True),
        ({DEV_AUTH_ENV_VAR: "1", LOCAL_EE_ENV_VAR: "1"}, True),
        ({DEV_AUTH_ENV_VAR: "false", LOCAL_EE_ENV_VAR: "false"}, False),
        (SANDBOX, False),
    ],
)
def test_plan_reads_sepal_headers_enumerates_every_arming_rule(env, expected):
    """A rule that reads the headers without appearing here sees a hardcoded False.

    This predicate is what makes callers pay to parse headers. Miss a rule and
    its interlock does not stop working loudly -- it stops working silently.
    """
    assert plan_reads_sepal_headers(env) is expected


def test_local_ee_does_not_reopen_the_headerless_fallback():
    """``PYSEPAL_LOCAL_EE`` reaches the credentials R2 exists to keep away.

    The difference is that it is armed by hand and demoted by real headers, so
    it can never be *reached* by a container degrading. Both halves are pinned
    here: unarmed stays PER_CONNECTION, armed-with-headers stays PER_CONNECTION.
    """
    assert _plan(using_solara_server=True).source is SessionSource.PER_CONNECTION
    assert (
        _plan(env={LOCAL_EE_ENV_VAR: "1"}, using_solara_server=True, has_sepal_headers=True).source
        is SessionSource.PER_CONNECTION
    )


def test_local_ee_still_validates_the_connection_headers(monkeypatch):
    """The interlock is only real if something actually parses the headers.

    ``_current_plan`` skips validation whenever no arming flag reads them. If
    that gate ever narrows back to ``PYSEPAL_DEV_AUTH`` alone, rule 3 keeps
    firing but ``has_sepal_headers`` arrives as a hardcoded False -- so a real
    user in a container with a stray ``PYSEPAL_LOCAL_EE`` is handed the shared
    process session instead of their own, and nothing else goes red.
    """
    import solara

    from pysepal.solara import session_manager as sm

    monkeypatch.delenv(DEV_AUTH_ENV_VAR, raising=False)
    monkeypatch.setenv(LOCAL_EE_ENV_VAR, "1")
    monkeypatch.setattr(solara, "_using_solara_server", lambda: True)

    monkeypatch.setattr(sm, "_carries_sepal_headers", lambda: True)
    assert sm._current_plan().source is SessionSource.PER_CONNECTION

    monkeypatch.setattr(sm, "_carries_sepal_headers", lambda: False)
    assert sm._current_plan().source is SessionSource.PROCESS


def test_using_solara_server_stays_false_under_pytest_and_voila():
    """Tripwire on the one probe that can flip the whole process to PER_CONNECTION.

    ``solara._using_solara_server`` is a *module-import* signal, not a runtime
    one: it is True as soon as ``solara.server.starlette`` or
    ``solara.server.flask`` is in ``sys.modules``, or ``sys.argv[0]`` is
    ``solara``. Importing solara's kernel machinery -- which pytest, Voila and
    plain Jupyter all do -- must not trip it, or every one of those runtimes
    would resolve as an app-launcher container and start raising on missing
    headers. If a solara upgrade or a stray starlette import changes this, it
    must fail here rather than in production.
    """
    import solara.server.app
    import solara.server.kernel_context as kernel_context

    context = kernel_context.create_dummy_context()
    kernel_context.set_current_context(context)
    try:
        assert "solara.server.starlette" not in sys.modules
        assert "solara.server.flask" not in sys.modules
        assert solara._using_solara_server() is False
        plan = current_session_plan(has_sepal_headers=False)
        assert plan.source is not SessionSource.PER_CONNECTION
    finally:
        kernel_context.set_current_context(None)


def test_the_probe_still_detects_a_running_solara_server():
    """The other half of the tripwire: a probe that stops saying True is silent.

    The test above only pins the safe direction -- the probe staying False
    where it must. A probe that silently stopped detecting a real Solara
    server would fail nothing there: every row of ``test_topology_table``
    would keep passing, and an app-launcher container would quietly start
    resolving PROCESS -- every user sharing one platform identity, with no
    test red anywhere. This pins the other direction by staging the exact
    ``sys.modules`` state the probe's first branch reads.
    """
    import types

    import solara

    sys.modules["solara.server.starlette"] = types.ModuleType("solara.server.starlette")
    try:
        assert solara._using_solara_server() is True
    finally:
        del sys.modules["solara.server.starlette"]
