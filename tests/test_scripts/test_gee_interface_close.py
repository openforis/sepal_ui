"""GEEInterface.close() must release the EESession HTTP client deterministically.

The EESession owns an ``httpx.AsyncClient`` (HTTP/2 pool, sockets, TLS state).
Before this test existed, ``close()`` stopped the loop and thread but never
called ``session.aclose()``, leaving the pool to whenever the garbage collector
ran. Cleanup on kernel cull must be deterministic.

No GEE credentials required: the session is a stub.
"""

import threading

from pysepal.scripts.gee_interface import GEEInterface


class StubSession:
    """Stands in for EESession — only ``aclose()`` matters here."""

    def __init__(self):
        """Track aclose() invocations and the thread they ran on."""
        self.aclose_calls = 0
        self.aclose_thread = None

    async def aclose(self):
        self.aclose_calls += 1
        self.aclose_thread = threading.current_thread()


class ExplodingSession(StubSession):
    async def aclose(self):
        await super().aclose()
        raise RuntimeError("boom")


def test_close_acloses_session() -> None:
    """close() awaits session.aclose() on the interface loop, then shuts down."""
    session = StubSession()
    iface = GEEInterface(session=session)

    iface.close()

    assert session.aclose_calls == 1
    # ran on the interface's own loop thread, i.e. BEFORE the loop was stopped
    assert session.aclose_thread is iface._async_thread
    assert iface._async_loop.is_closed()


def test_close_without_session() -> None:
    """close() still shuts the loop down cleanly when there is no session."""
    iface = GEEInterface()

    iface.close()

    assert iface._async_loop.is_closed()


def test_close_survives_aclose_error_and_is_idempotent() -> None:
    """An aclose() failure must not block shutdown; close() twice is a no-op."""
    session = ExplodingSession()
    iface = GEEInterface(session=session)

    iface.close()  # must not raise
    iface.close()  # idempotent

    assert session.aclose_calls == 1
    assert iface._async_loop.is_closed()
