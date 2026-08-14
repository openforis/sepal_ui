"""``SepalMap(gee=True)`` must not reach the machine's credentials per connection.

The map is the second door into the shared platform identity that pysepal 4.0
closes in the session layer: with no ``gee_interface`` it builds a session-less
``GEEInterface`` and calls ``su.init_ee()``, which reads
``~/.config/earthengine/credentials`` -- the *platform* service-account key in an
app-launcher container. Refused only where a runtime serves one identity per
connection; a notebook or sandbox owns those credentials and keeps them.
"""

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pysepal import mapping as sm
from pysepal.mapping import sepal_map as sepal_map_module
from pysepal.solara import session_manager as session_manager_module
from pysepal.solara._topology import SessionPlan, SessionSource
from pysepal.solara.errors import SepalSessionError

PER_CONNECTION = SessionPlan(SessionSource.PER_CONNECTION, "test")
PROCESS = SessionPlan(SessionSource.PROCESS, "test")
DEV_AUTH = SessionPlan(SessionSource.DEV_AUTH, "test")


@contextmanager
def _topology(plan):
    """Stage a runtime with both Earth Engine side effects stubbed out.

    ``GEEInterface`` starts an event-loop thread in its constructor and
    ``init_ee`` calls ``ee.Initialize()``, so counting the calls is also how
    these tests assert that neither happened.
    """
    init_ee = MagicMock()
    gee_interface = MagicMock(side_effect=lambda **kwargs: MagicMock())

    with (
        patch.object(session_manager_module, "_current_plan", return_value=plan),
        patch.object(sepal_map_module.su, "init_ee", init_ee),
        patch.object(sepal_map_module, "GEEInterface", gee_interface),
    ):
        yield SimpleNamespace(init_ee=init_ee, gee_interface=gee_interface)


def test_a_per_connection_runtime_refuses_the_ambient_credentials():
    """The whole point: the container must not render on the platform account."""
    with _topology(PER_CONNECTION) as stubs:
        with pytest.raises(SepalSessionError, match="gee_interface"):
            sm.SepalMap()

    # Refused *before* either side effect: a raise that still started a thread
    # and initialised the global ``ee`` would leak both on every render.
    assert stubs.gee_interface.call_count == 0
    assert stubs.init_ee.call_count == 0


def test_an_explicit_interface_is_always_allowed():
    """The correct call in an app-launcher container, and the fix the error names."""
    supplied = MagicMock()

    with _topology(PER_CONNECTION) as stubs:
        map_ = sm.SepalMap(gee_interface=supplied)

    assert map_.gee_interface is supplied
    assert stubs.gee_interface.call_count == 0


def test_an_explicit_session_is_always_allowed():
    """A caller-supplied session is a real identity; only the ambient one is refused."""
    with _topology(PER_CONNECTION) as stubs:
        sm.SepalMap(gee_session=MagicMock())

    assert stubs.gee_interface.call_count == 1


def test_gee_false_never_reaches_the_guard():
    with _topology(PER_CONNECTION) as stubs:
        map_ = sm.SepalMap(gee=False)

    assert not hasattr(map_, "gee_interface")
    assert stubs.init_ee.call_count == 0


@pytest.mark.parametrize("plan", [PROCESS, DEV_AUTH], ids=["process", "dev_auth"])
def test_a_single_identity_runtime_keeps_the_ambient_credentials(plan):
    """Voila, Jupyter, a sandbox and a script own their machine credentials.

    ``SepalMap()`` in a notebook is the documented quickstart and the example in
    ``pysepal.mapping``'s own docstring; narrowing the guard beyond
    PER_CONNECTION would break it for no safety gain.
    """
    with _topology(plan) as stubs:
        sm.SepalMap()

    assert stubs.gee_interface.call_count == 1
    assert stubs.init_ee.call_count == 1


def test_the_guard_is_inert_under_a_real_plain_runtime():
    """No plan patched: pytest resolves PROCESS, so nothing about ``SepalMap()`` changes.

    The compatibility half of this feature. Every other test here stages a
    topology; this one pins that the guard stays out of the way when the real
    resolver runs, which is what the 84 existing ``SepalMap()`` call sites rely on.
    """
    with (
        patch.object(sepal_map_module.su, "init_ee", MagicMock()),
        patch.object(sepal_map_module, "GEEInterface", MagicMock()),
    ):
        sm.SepalMap()
