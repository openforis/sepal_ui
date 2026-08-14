"""Reading a session's status must not race the render that is filling it in.

``_session_info_for`` reads a *live* session dict field by field, while
``_ensure_sepal_client`` mutates it on another connection's render thread. The
reads are separate bytecodes, so without the scope lock a caller can be handed a
``SessionInfo`` assembled from both sides of a concurrent write -- an
``active_module_name`` absent from ``module_names``, which is an admin panel
reporting a state the process was never in.

Two things this is deliberately *not*:

- Not a ``RuntimeError`` from ``sorted(clients)``. That is the intuitive guess
  and it is unreachable: ``list(dict)`` is a single C call that holds the GIL for
  its whole duration, so no pure-Python thread can resize the dict mid-iteration.
  Measured at a 1e-9 switch interval, 20000 reads against 4 writers: zero.
- Not a statistical race. The window is the handful of bytecodes between two
  adjacent ``.get()`` calls; the same measurement found zero tears in 20000
  unlocked reads. So the writer is released at the exact point instead, the way
  ``test_singleton_construction`` blocks inside ``__init__``.
"""

import threading

import pytest

from pysepal.solara.session_manager import SessionManager

SCOPE = "kernel-a"
BASE_MODULE = "seed-0"
DOOMED_MODULE = "module-x"

WRITER_WINDOW = 0.2
"""How long the read waits for the writer. Spent in full when the lock works."""


class _TripwireSession(dict):
    """A session dict that lets a writer run at one exact point of the read.

    ``_session_info_for`` reads ``active_module_name`` after it has taken its
    reference to ``sepal_clients`` but before it iterates it, so that is the
    only point where a write can tear the snapshot. Intercepting the read is
    what turns a rare interleaving into a deterministic one.
    """

    def __init__(self, *args, on_active_read=lambda: None, **kwargs):
        super().__init__(*args, **kwargs)
        self._on_active_read = on_active_read

    def get(self, key, default=None):
        if key == "active_module_name":
            self._on_active_read()
        return super().get(key, default)


@pytest.fixture
def racing_read():
    """A session whose status read releases a competing writer mid-flight."""
    manager = SessionManager()
    release = threading.Event()
    finished = threading.Event()

    session = _TripwireSession(
        {
            "username": "alice",
            "gee_interface": object(),
            "drive_interface": None,
            "sepal_clients": {BASE_MODULE: object(), DOOMED_MODULE: object()},
            "active_module_name": DOOMED_MODULE,
        },
        on_active_read=lambda: (release.set(), finished.wait(timeout=WRITER_WINDOW)),
    )
    manager._registry.set(session, SCOPE)
    lock = manager._registry.scope_lock(SCOPE)

    def _retire_the_active_module() -> None:
        assert release.wait(timeout=5), "the read never reached active_module_name"
        # Exactly what _ensure_sepal_client does: mutate under the scope lock.
        with lock:
            session["sepal_clients"].pop(DOOMED_MODULE, None)
        finished.set()

    writer = threading.Thread(target=_retire_the_active_module)
    writer.start()
    try:
        yield manager
    finally:
        release.set()
        finished.set()
        writer.join(timeout=5)


def test_a_status_read_is_not_assembled_from_two_different_states(racing_read):
    """The writer must not land between the two reads that have to agree.

    Holding the scope lock, the reader blocks the writer for ``WRITER_WINDOW``
    and reports the state it started from. Without it the writer retires
    ``module-x`` in that gap, and the snapshot names an active module that its
    own ``module_names`` does not contain.
    """
    info = racing_read._session_info_for(SCOPE)

    assert info.active_module_name in info.module_names, (
        f"snapshot torn: active={info.active_module_name!r} "
        f"is absent from module_names={info.module_names!r}"
    )


def test_the_overview_reads_every_scope_the_same_way():
    """``sessions_overview`` reaches the same reader, so it inherits the lock."""
    manager = SessionManager()
    for index in range(3):
        manager._registry.set(
            {
                "username": "alice",
                "gee_interface": object(),
                "drive_interface": None,
                "sepal_clients": {BASE_MODULE: object()},
                "active_module_name": BASE_MODULE,
            },
            f"kernel-{index}",
        )

    overview = manager.sessions_overview()

    assert {info.scope_id for info in overview.sessions} == {f"kernel-{i}" for i in range(3)}
    assert all(info.active_module_name in info.module_names for info in overview.sessions)
