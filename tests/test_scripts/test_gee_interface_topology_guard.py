"""A session-less ``GEEInterface`` is refused where the process serves many users.

Every method on the interface is written ``if self.session: ... else: <global
ee>``, so no session means the whole API answers from
``~/.config/earthengine/credentials`` -- the platform service-account key in an
app-launcher container. The guard lives in the constructor rather than in each
caller because ``gee_interface or GEEInterface()`` appears in seven places
across four subpackages, and that list only grows.
"""

import inspect
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pysepal.scripts import gee_interface as gee_interface_module
from pysepal.scripts.gee_interface import GEEInterface
from pysepal.solara import session_manager as session_manager_module
from pysepal.solara._topology import SessionPlan, SessionSource
from pysepal.solara.errors import SepalSessionError

PER_CONNECTION = SessionPlan(SessionSource.PER_CONNECTION, "test")
PROCESS = SessionPlan(SessionSource.PROCESS, "test")
DEV_AUTH = SessionPlan(SessionSource.DEV_AUTH, "test")


@contextmanager
def _topology(plan):
    """Stage a runtime and count event loops, which is how the leak is asserted."""
    new_event_loop = MagicMock(side_effect=lambda: MagicMock())

    with (
        patch.object(session_manager_module, "_current_plan", return_value=plan),
        patch.object(gee_interface_module.asyncio, "new_event_loop", new_event_loop),
        patch.object(gee_interface_module.threading, "Thread", MagicMock()),
    ):
        yield SimpleNamespace(new_event_loop=new_event_loop)


def test_a_per_connection_runtime_refuses_a_session_less_interface():
    with _topology(PER_CONNECTION) as stubs:
        with pytest.raises(SepalSessionError, match="platform service account"):
            GEEInterface()

    # Refused before the loop exists. A guard that raised afterwards would leak
    # one event loop and one daemon thread per attempt, forever.
    assert stubs.new_event_loop.call_count == 0


def test_a_session_bound_interface_is_always_allowed():
    """The correct construction in a container: built from this connection's session."""
    session = MagicMock()

    with _topology(PER_CONNECTION):
        interface = GEEInterface(session=session)

    assert interface.session is session


@pytest.mark.parametrize("plan", [PROCESS, DEV_AUTH], ids=["process", "dev_auth"])
def test_a_single_identity_runtime_keeps_the_global_ee_path(plan):
    """A notebook, a script, pytest and a sandbox own their machine credentials.

    The global-``ee`` fallback is the normal path there, and narrowing the guard
    past PER_CONNECTION would break every one of them for no safety gain.
    """
    with _topology(plan) as stubs:
        interface = GEEInterface()

    assert interface.session is None
    assert stubs.new_event_loop.call_count == 1


def test_the_use_sepal_headers_door_is_gone():
    """The one constructor path that built an identity this guard could not see.

    ``GEEInterface(use_sepal_headers=True)`` logged in from
    ``LOCAL_SEPAL_USER``/``LOCAL_SEPAL_PASSWORD`` and assigned the result to
    ``session``, so ``session is None`` was already False by the time the guard
    ran -- one process-wide developer identity, served in any runtime including
    a multi-user container. It had no callers in pysepal, in the tests, or in
    any downstream module, and 4.0 removes it; ``PYSEPAL_DEV_AUTH`` is the
    supported way to run on a developer login, and it goes through topology.
    """
    assert "use_sepal_headers" not in inspect.signature(GEEInterface.__init__).parameters

    with pytest.raises(TypeError, match="use_sepal_headers"):
        GEEInterface(use_sepal_headers=True)


def test_the_guard_is_inert_under_a_real_plain_runtime():
    """No plan patched: pytest resolves PROCESS, so ``GEEInterface()`` is unchanged.

    The compatibility half. Every other test here stages a topology; this one
    runs the real resolver, which is what the existing bare ``GEEInterface()``
    call sites in ``scripts.gee``, ``mapping.visualization`` and the test
    fixtures rely on.
    """
    interface = GEEInterface()
    try:
        assert interface.session is None
    finally:
        interface.close()
