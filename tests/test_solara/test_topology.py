"""Tests for the runtime-topology rules deciding a session's credential source."""

import sys

import pytest

from pysepal.solara._topology import (
    DEV_AUTH_ENV_VAR,
    SessionSource,
    current_session_plan,
    dev_auth_enabled,
    is_sepal_sandbox,
    resolve_session_plan,
)


def _plan(**overrides):
    kwargs = {
        "env": {},
        "home_name": "developer",
        "using_solara_server": False,
        "has_sepal_headers": False,
    }
    kwargs.update(overrides)
    return resolve_session_plan(**kwargs)


@pytest.mark.parametrize(
    ("env", "home_name", "using_solara_server", "has_sepal_headers", "expected"),
    [
        # app-manager app: the sandbox's own credentials are the user's own
        ({}, "sepal-user", False, False, SessionSource.PROCESS),
        ({}, "sepal-user", True, False, SessionSource.PROCESS),
        ({}, "sepal-user", True, True, SessionSource.PROCESS),
        # app-launcher container: one identity per connection, never shared
        ({}, "developer", True, False, SessionSource.PER_CONNECTION),
        ({}, "developer", True, True, SessionSource.PER_CONNECTION),
        # voila, plain jupyter, a script, pytest
        ({}, "developer", False, False, SessionSource.PROCESS),
        # headers alone never select PER_CONNECTION -- only dev-auth reads them
        ({}, "developer", False, True, SessionSource.PROCESS),
        # dev auth arms a single process-wide login...
        ({DEV_AUTH_ENV_VAR: "1"}, "developer", True, False, SessionSource.DEV_AUTH),
        ({DEV_AUTH_ENV_VAR: "true"}, "developer", False, False, SessionSource.DEV_AUTH),
        ({DEV_AUTH_ENV_VAR: "1"}, "sepal-user", False, False, SessionSource.DEV_AUTH),
        # ...but real SEPAL headers always demote it
        ({DEV_AUTH_ENV_VAR: "1"}, "developer", True, True, SessionSource.PER_CONNECTION),
        # a disarmed value is not an arming value
        ({DEV_AUTH_ENV_VAR: "false"}, "developer", True, False, SessionSource.PER_CONNECTION),
        ({DEV_AUTH_ENV_VAR: ""}, "developer", True, False, SessionSource.PER_CONNECTION),
    ],
)
def test_topology_table(env, home_name, using_solara_server, has_sepal_headers, expected):
    plan = resolve_session_plan(
        env=env,
        home_name=home_name,
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
    assert _plan(home_name="sepal-user", using_solara_server=True).source is SessionSource.PROCESS


@pytest.mark.parametrize(
    ("env", "home_name", "using_solara_server", "has_sepal_headers", "reason_substring"),
    [
        ({DEV_AUTH_ENV_VAR: "1"}, "developer", False, False, DEV_AUTH_ENV_VAR),
        ({}, "sepal-user", False, False, "sandbox"),
        ({}, "developer", True, False, "Solara server"),
        ({}, "developer", False, False, "no Solara server"),
    ],
)
def test_the_reason_names_the_rule_that_fired(
    env, home_name, using_solara_server, has_sepal_headers, reason_substring
):
    """A truthy ``reason`` isn't enough -- it must name the rule that actually fired."""
    plan = resolve_session_plan(
        env=env,
        home_name=home_name,
        using_solara_server=using_solara_server,
        has_sepal_headers=has_sepal_headers,
    )

    assert reason_substring in plan.reason


@pytest.mark.parametrize(
    ("home_name", "expected"),
    [
        ("sepal-user", True),
        ("sepal-user-backup", False),
        ("notsepal-user", False),
        ("my-sepal-user-data", False),
        ("developer", False),
        ("", False),
    ],
)
def test_is_sepal_sandbox(home_name, expected):
    assert is_sepal_sandbox(home_name) is expected


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
