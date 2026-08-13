"""``SessionManager()`` must hand every racing thread the same, ready manager.

The registry and the tombstone deque are *instance* attributes -- test
isolation depends on that (``conftest._reset_session_manager``) -- so a lost
construction race does not merely waste an object, it splits the state. The
orphan's sessions are never cleaned up, its ``GEEInterface`` keeps a private
event-loop thread alive forever, and the tombstones it writes are read by
nobody, so a cleaned-up scope becomes resurrectable. ``setup_sessions()`` runs
on concurrent kernel-start threads, so the window is real.

Two tests, because the two halves are not equally reachable. ``__init__`` can
be raced deterministically by blocking inside it. ``__new__`` cannot -- nothing
in it is patchable without replacing the code under test -- so it is raced
statistically: threads released from one barrier with the switch interval at
its floor. Measured against the unlocked code on the maintainer's machine,
a round hits 3-5% of the time at 32 threads, so 400 rounds leave a miss
probability under 1e-5.
"""

import sys
import threading

import pytest

from pysepal.solara import session_manager as sm
from pysepal.solara.session_manager import SessionManager

THREADS = 32
"""Racing threads per round; below ~32 the observed hit rate drops tenfold."""

ROUNDS = 400
"""Enough rounds that a miss is ~1e-5. Costs about a second."""


@pytest.fixture
def eager_thread_switches():
    """Switch threads as often as CPython allows, to widen the race window.

    The trace hook has to go with it. Under ``--cov`` on Python <= 3.11,
    coverage measures threads by installing a C trace function through
    ``threading.settrace``, so each of the 12800 threads below is born traced
    and every line it runs is measured -- with the switch interval at its floor
    this does not finish in any useful time, which is exactly how CI hung on
    3.10 and 3.11 while 3.12 passed in seconds. 3.12 escapes because coverage
    switches to :mod:`sys.monitoring` (PEP 669), which costs nothing per thread.

    Only threads started inside the fixture are affected; the main thread keeps
    its own tracing, and the code these threads exercise is covered by the rest
    of this module either way.
    """
    original_interval = sys.getswitchinterval()
    original_trace = threading.gettrace()
    original_profile = threading.getprofile()

    threading.settrace(None)
    threading.setprofile(None)
    sys.setswitchinterval(1e-9)
    try:
        yield
    finally:
        sys.setswitchinterval(original_interval)
        threading.settrace(original_trace)
        threading.setprofile(original_profile)


def race_to_construct(threads: int) -> tuple[list[SessionManager], list[BaseException]]:
    """Construct ``SessionManager`` from ``threads`` threads released together.

    Every thread registers a scope of its own through the manager it was
    handed. A split registry loses those writes silently, which is the harm
    worth asserting on -- not merely that two objects exist.

    Args:
        threads: How many threads race into the constructor.

    Returns:
        The managers handed out, and anything the workers raised.
    """
    start = threading.Barrier(threads)
    built: list[SessionManager] = []
    failures: list[BaseException] = []

    def _worker(index: int) -> None:
        start.wait()
        try:
            manager = SessionManager()
            manager._registry.set({"worker": index}, scope_id=f"scope-{index}")
            built.append(manager)  # list.append is atomic under the GIL
        except BaseException as exc:  # collected, then asserted on
            failures.append(exc)

    workers = [threading.Thread(target=_worker, args=(index,)) for index in range(threads)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()
    return built, failures


def test_concurrent_construction_yields_one_ready_manager(eager_thread_switches):
    """Two managers means two registries, and one of them is an orphan.

    A thread holding the orphan gets ``SepalSessionError`` for a session it
    just created, and nothing will ever call ``cleanup_session`` on it.
    """
    expected_scopes = {f"scope-{index}" for index in range(THREADS)}

    for round_number in range(ROUNDS):
        SessionManager._instance = None

        built, failures = race_to_construct(THREADS)

        assert failures == [], f"round {round_number}"
        assert len({id(manager) for manager in built}) == 1, f"round {round_number}"
        live_scopes = set(SessionManager._instance._registry.scope_ids())
        assert live_scopes == expected_scopes, f"round {round_number}"


def test_a_second_constructor_waits_for_a_half_built_manager(monkeypatch):
    """The ``_initialized`` guard must run under the lock ``__new__`` takes.

    ``__new__`` hands the second thread the same object while the first is
    still inside ``__init__``. Locking only ``__new__`` moves the race rather
    than closing it: the second thread would either build a second registry
    over the first, or -- ordering the flag before the state -- return a
    manager whose ``_registry`` does not exist yet.
    """
    building = threading.Event()
    release = threading.Event()
    registries_built = []
    real_scope_registry = sm.ScopeRegistry

    def _blocking_scope_registry(*args, **kwargs):
        registries_built.append(1)
        if len(registries_built) == 1:
            building.set()
            assert release.wait(timeout=5)
        return real_scope_registry(*args, **kwargs)

    monkeypatch.setattr(sm, "ScopeRegistry", _blocking_scope_registry)

    first = threading.Thread(target=SessionManager)
    first.start()
    assert building.wait(timeout=5), "the first constructor never reached the registry"

    handed_out = []
    second = threading.Thread(target=lambda: handed_out.append(SessionManager()))
    second.start()
    second.join(timeout=0.2)
    assert second.is_alive(), "the second constructor was handed a half-built manager"

    release.set()
    first.join(timeout=5)
    second.join(timeout=5)

    assert registries_built == [1], "the manager was initialized twice"
    assert handed_out[0] is SessionManager._instance
    assert handed_out[0]._registry is not None
