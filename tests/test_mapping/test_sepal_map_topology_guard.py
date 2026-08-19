"""``SepalMap`` inherits the ``GEEInterface`` guard rather than carrying its own.

The map was the most reachable way into the shared platform identity:
``SepalMap(gee=True)`` is the default, and with no ``gee_interface`` it builds a
session-less ``GEEInterface`` and calls ``su.init_ee()``. The refusal now lives
in the ``GEEInterface`` constructor (see
``tests/test_scripts/test_gee_interface_topology_guard.py``); these tests pin
that the map actually inherits it, and that it does so *before* ``init_ee()``
touches the global ``ee``.
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


@contextmanager
def _topology(plan):
    """Stage a runtime with only ``init_ee`` stubbed.

    ``GEEInterface`` is deliberately left real: it is the thing under test here,
    and a mock would make every one of these tests pass whether the map inherits
    the guard or not.
    """
    init_ee = MagicMock()

    with (
        patch.object(session_manager_module, "_current_plan", return_value=plan),
        patch.object(sepal_map_module.su, "init_ee", init_ee),
    ):
        yield SimpleNamespace(init_ee=init_ee)


def test_a_per_connection_runtime_refuses_the_default_map():
    """`SepalMap()` in an app-launcher container must not render on the platform account."""
    with _topology(PER_CONNECTION) as stubs:
        with pytest.raises(SepalSessionError, match="platform service account"):
            sm.SepalMap()

    # init_ee() is what initialises the global ee from the container's
    # credentials file. Refusing after it had run would close the interface
    # door while leaving the global one open.
    assert stubs.init_ee.call_count == 0


def test_an_explicit_interface_is_always_allowed():
    """The fix the error names, and what the map app template already does."""
    supplied = MagicMock()

    with _topology(PER_CONNECTION):
        map_ = sm.SepalMap(gee_interface=supplied)

    assert map_.gee_interface is supplied


def test_gee_false_builds_no_interface_at_all():
    with _topology(PER_CONNECTION) as stubs:
        map_ = sm.SepalMap(gee=False)

    assert not hasattr(map_, "gee_interface")
    assert stubs.init_ee.call_count == 0


def test_a_single_identity_runtime_keeps_the_default_map():
    """`SepalMap()` in a notebook is the quickstart and the docstring example."""
    with _topology(PROCESS) as stubs:
        map_ = sm.SepalMap()

    # Built, but no credential read yet: resolution waits for the first call.
    assert map_.gee_interface is not None
    assert map_.gee_interface._session is None
    assert stubs.init_ee.call_count == 1
    map_.gee_interface.close()
