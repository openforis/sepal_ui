"""Tests for SessionManager.create_session hardening (locking, identity, tombstone)."""

import threading
import time
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pysepal.solara import session_manager as sm
from pysepal.solara._topology import SessionPlan, SessionSource
from pysepal.solara.errors import (
    MissingSepalHeadersError,
    SepalSessionError,
    SessionScopeClosedError,
)
from pysepal.solara.runtime_context import PROCESS_SCOPE
from pysepal.solara.session_manager import SessionManager

_MISSING = object()

_PER_CONNECTION_PLAN = SessionPlan(SessionSource.PER_CONNECTION, "test")
_PROCESS_PLAN = SessionPlan(SessionSource.PROCESS, "test")


def _validation_error():
    from pydantic import BaseModel, ValidationError

    class _Probe(BaseModel):
        required: str

    try:
        _Probe.model_validate({})
    except ValidationError as exc:
        return exc
    raise AssertionError("expected a ValidationError")


def _parsed_headers(username="alice", session_id="sid-1"):
    return SimpleNamespace(
        sepal_user=SimpleNamespace(username=username),
        cookies={"SEPAL-SESSIONID": session_id},
        session_id=session_id,
    )


@contextmanager
def _stack(username="alice", session_id="sid-1", raw_headers=_MISSING, gee_delay=0.0):
    """Patch every external constructor create_session reaches for.

    Yields a namespace of the patched factories so call counts stay readable.
    ``raw_headers=None`` means "this connection has no headers"; omitting it
    supplies a plausible header dict.
    """
    header_value = {"cookie": ["x"]} if raw_headers is _MISSING else raw_headers
    parsed = _parsed_headers(username, session_id)

    def _build_gee(*_args, **_kwargs):
        if gee_delay:
            time.sleep(gee_delay)
        return MagicMock()

    gee_factory = MagicMock(side_effect=_build_gee)
    sepal_factory = MagicMock(
        side_effect=lambda **kwargs: SimpleNamespace(
            ensure_results_dir=MagicMock(), module_name=kwargs.get("module_name"), close=MagicMock()
        )
    )
    drive_factory = MagicMock(side_effect=lambda **kwargs: MagicMock())

    with (
        patch.object(sm, "_current_plan", return_value=_PER_CONNECTION_PLAN),
        patch.object(sm, "resolve_scope_id", return_value="kernel-a"),
        patch.object(sm, "headers", SimpleNamespace(value=header_value)),
        patch.object(sm, "SepalHeaders", SimpleNamespace(model_validate=lambda _v: parsed)),
        patch.object(sm, "EESession", SimpleNamespace(from_sepal_headers=lambda _h: MagicMock())),
        patch.object(sm, "GEEInterface", gee_factory),
        patch.object(sm, "SepalClient", SimpleNamespace(create=sepal_factory)),
        patch.object(sm, "GDriveInterface", drive_factory),
        patch.object(sm, "_RESULTS_DIR_EXECUTOR", SimpleNamespace(submit=lambda fn: fn())),
    ):
        yield SimpleNamespace(gee=gee_factory, sepal=sepal_factory, drive=drive_factory)


def test_typed_accessors_dispatch_on_topology():
    """No public accessor takes a session-dict key as a string.

    And none of them falls back: PER_CONNECTION with no session is a bug,
    not a default.
    """
    manager = SessionManager()
    assert not hasattr(manager, "get_session_component")
    with _stack():
        with pytest.raises(SepalSessionError, match="with_sepal_sessions"):
            manager.get_gee_interface()

        manager.create_session(module_name="route_a")
        session = manager._registry.get("kernel-a")
        assert manager.get_gee_interface() is session["gee_interface"]
        assert manager.get_drive_interface() is session["drive_interface"]
        assert manager.get_sepal_client("route_a") is not None


def test_create_session_refuses_the_reserved_process_scope():
    """Solara's kernel id is client-supplied; ``process`` is not allowlisted.

    A connection landing on scope id ``PROCESS_SCOPE`` must not create or
    reuse a per-connection session there -- that key belongs to the shared
    process/dev-auth session, and this is the write-side half of the same
    collision ``_require_connection_session`` refuses on the read side.
    """
    manager = SessionManager()
    with _stack():
        with patch.object(sm, "resolve_scope_id", return_value=PROCESS_SCOPE):
            with pytest.raises(SepalSessionError, match="reserved process scope"):
                manager.create_session()

    assert PROCESS_SCOPE not in manager.session_scope_ids()


def test_missing_headers_raise_instead_of_returning_silently():
    manager = SessionManager()
    with _stack(raw_headers=None):
        with pytest.raises(MissingSepalHeadersError, match="kernel-a"):
            manager.create_session()

    assert manager.session_scope_ids() == ()


def test_same_identity_reuses_the_session():
    manager = SessionManager()
    with _stack() as factories:
        manager.create_session()
        manager.create_session()

        assert factories.gee.call_count == 1


def test_repeat_renders_do_not_reparse_the_headers():
    """create_session runs on every render; the fast path must skip parsing."""
    manager = SessionManager()
    calls = []
    with _stack():
        with patch.object(sm, "resolve_sepal_headers", wraps=sm.resolve_sepal_headers) as spy:
            manager.create_session()
            manager.create_session()
            manager.create_session()
            calls = spy.call_args_list

    assert len(calls) == 1


def test_reconnect_with_new_headers_object_reuses_the_session():
    """A websocket reconnect hands back a new headers object with the same identity."""
    manager = SessionManager()
    with _stack(username="alice", session_id="sid-1") as factories:
        manager.create_session()
        first_headers = sm.headers.value

        sm.headers.value = {"cookie": ["y"]}
        assert sm.headers.value is not first_headers

        manager.create_session()

        assert factories.gee.call_count == 1
        assert manager._registry.get("kernel-a")["raw_headers"] is sm.headers.value


def test_a_new_route_after_a_reconnect_still_gets_its_own_client():
    """The identity-match branch, not the raw-header fast path."""
    manager = SessionManager()
    with _stack() as factories:
        manager.create_session(module_name="route_a")
        first = manager.get_sepal_client("route_a")

        sm.headers.value = {"cookie": ["y"]}
        manager.create_session(module_name="route_b")

        assert factories.gee.call_count == 1
        assert factories.sepal.call_count == 2
        assert manager.get_sepal_client("route_b") is not first


def test_changed_sepal_session_id_rebuilds_the_session():
    """A recycled scope must never inherit the previous identity's interfaces."""
    manager = SessionManager()
    with _stack(username="alice", session_id="sid-1") as first_factories:
        manager.create_session(module_name="route_a")
        manager.create_session(module_name="route_b")
        first = manager.get_gee_interface()
        first_clients = [manager.get_sepal_client("route_a"), manager.get_sepal_client("route_b")]

        assert first_factories.gee.call_count == 1

    with _stack(username="bob", session_id="sid-2") as second_factories:
        manager.create_session()
        second = manager.get_gee_interface()

        assert second_factories.gee.call_count == 1

    assert second is not first
    first.close.assert_called_once()
    for client in first_clients:
        client.close.assert_called_once()
    assert manager.get_session_info("kernel-a").username == "bob"


def test_identity_rebuild_failure_does_not_leave_a_closed_session_reachable():
    """A construction failure after the identity flip must not strand a closed session."""
    manager = SessionManager()
    with _stack(username="alice", session_id="sid-1"):
        manager.create_session()
        old_gee = manager.get_gee_interface()

    with _stack(username="bob", session_id="sid-2") as factories:
        factories.gee.side_effect = RuntimeError("boom")

        with pytest.raises(RuntimeError):
            manager.create_session()

    assert "kernel-a" not in manager.session_scope_ids()
    old_gee.close.assert_called_once()


def test_concurrent_first_renders_build_one_gee_interface():
    """Two GEEInterfaces means two private event loops, one of them orphaned."""
    manager = SessionManager()
    start = threading.Barrier(4)

    with _stack(gee_delay=0.05) as factories:

        def _worker():
            start.wait()
            manager.create_session()

        threads = [threading.Thread(target=_worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert factories.gee.call_count == 1


def test_closed_scope_cannot_be_resurrected():
    """A late callback on the GEE loop thread must not rebuild a dead scope."""
    manager = SessionManager()
    with _stack():
        manager.create_session()
        manager.cleanup_session("kernel-a")

        with pytest.raises(SessionScopeClosedError, match="kernel-a"):
            manager.create_session()


def test_setup_sessions_reopens_a_tombstoned_scope_on_restart():
    """Solara's hot-reload restart: same kernel id, cleanup then re-setup."""
    manager = SessionManager()
    with _stack() as factories:
        manager.create_session()

        cleanup = sm.setup_sessions()
        cleanup()

        with pytest.raises(SessionScopeClosedError, match="kernel-a"):
            manager.create_session()

        sm.setup_sessions()
        manager.create_session()

        assert factories.gee.call_count == 2


def test_reopen_scope_serializes_against_a_concurrent_cleanup():
    """A restart's reopen must never race a still-running cleanup for the same scope.

    ``cleanup_session`` writes the tombstone only after ``_close_session``
    returns, which can block for seconds closing the GEE interface. A reopen
    that isn't serialised against the whole cleanup -- not just the tombstone
    write -- can land in that window, find nothing to remove yet, and then
    lose the race when cleanup writes the tombstone moments later.
    """
    manager = SessionManager()
    with _stack() as factories:
        manager.create_session()
        gee_interface = manager.get_gee_interface()

        close_started = threading.Event()
        release_close = threading.Event()

        def _slow_close():
            close_started.set()
            release_close.wait(timeout=5.0)

        gee_interface.close.side_effect = _slow_close

        cleanup_thread = threading.Thread(target=manager.cleanup_session, args=("kernel-a",))
        cleanup_thread.start()
        assert close_started.wait(timeout=2.0)

        # cleanup_session is blocked inside _close_session right now, scope lock
        # held, tombstone not written yet. Dispatch the reopen on its own thread
        # (calling it from here would deadlock: nothing would ever set
        # release_close) and prove it blocks on the still-held scope lock rather
        # than racing through on the registry lock alone.
        reopen_thread = threading.Thread(target=manager._reopen_scope, args=("kernel-a",))
        reopen_thread.start()
        reopen_thread.join(timeout=0.2)
        assert reopen_thread.is_alive(), "_reopen_scope must block on the still-held scope lock"

        release_close.set()
        cleanup_thread.join(timeout=2.0)
        reopen_thread.join(timeout=2.0)
        assert not cleanup_thread.is_alive()
        assert not reopen_thread.is_alive()

        manager.create_session()

        assert factories.gee.call_count == 2


def test_partial_session_build_closes_already_built_interfaces():
    """A later constructor failing must not leak the interfaces built before it."""
    manager = SessionManager()
    with _stack() as factories:
        gee_built = MagicMock()
        sepal_built = MagicMock()

        with (
            patch.object(sm, "GEEInterface", return_value=gee_built),
            patch.object(
                sm, "SepalClient", SimpleNamespace(create=MagicMock(return_value=sepal_built))
            ),
        ):
            factories.drive.side_effect = RuntimeError("boom")

            with pytest.raises(RuntimeError):
                manager.create_session()

        gee_built.close.assert_called_once()
        sepal_built.close.assert_called_once()
        assert manager.session_scope_ids() == ()


def test_cleanup_closes_a_drive_interface_that_has_close():
    """ee-client 3.1.0 gives GDriveInterface a close(); cleanup must use it."""
    manager = SessionManager()
    with _stack() as factories:
        manager.create_session()
        drive = manager.get_drive_interface()
        manager.cleanup_session("kernel-a")

    assert factories.drive.call_count == 1
    drive.close.assert_called_once()


def test_cleanup_survives_a_drive_interface_that_fails_to_close():
    """A failed drive close must not skip the tombstone.

    ``cleanup_session`` writes the tombstone after ``_close_session``, inside
    the same scope lock; a close that escapes ``_close_session`` would skip it
    and break the invariant ``test_closed_scope_cannot_be_resurrected`` protects.
    """
    manager = SessionManager()
    with _stack() as factories:
        factories.drive.side_effect = lambda **kwargs: SimpleNamespace(
            close=MagicMock(side_effect=RuntimeError("boom"))
        )
        manager.create_session()
        manager.get_drive_interface()
        manager.cleanup_session("kernel-a")

    assert manager.session_scope_ids() == ()
    assert "kernel-a" in manager._closed_scopes


def test_creating_a_client_schedules_its_results_directory():
    """The per-connection path must schedule the directory too.

    Not only the process/sandbox path -- this is the deployed app-launcher
    container's own path.
    """
    manager = SessionManager()
    with _stack() as factories:
        manager.create_session(module_name="route_a")
        client = manager.get_sepal_client("route_a")

    assert factories.sepal.call_count == 1
    client.ensure_results_dir.assert_called_once()


def test_each_module_name_gets_its_own_client_on_one_session():
    """First-route-wins leak: 8 routes shared route 1's results directory."""
    manager = SessionManager()
    with _stack() as factories:
        manager.create_session(module_name="route_a")
        client_a = manager.get_sepal_client("route_a")
        manager.create_session(module_name="route_b")
        client_b = manager.get_sepal_client("route_b")

        assert client_a is not client_b
        assert factories.sepal.call_count == 2
        # Load-bearing: one GEEInterface, therefore one private event loop.
        assert factories.gee.call_count == 1


def test_the_last_entered_module_is_the_active_one():
    manager = SessionManager()
    with _stack():
        manager.create_session(module_name="route_a")
        manager.create_session(module_name="route_b")

        assert manager.get_sepal_client() is manager.get_sepal_client("route_b")


def test_revisiting_a_module_reuses_its_client():
    manager = SessionManager()
    with _stack() as factories:
        manager.create_session(module_name="route_a")
        first = manager.get_sepal_client("route_a")
        manager.create_session(module_name="route_b")
        manager.create_session(module_name="route_a")

        assert manager.get_sepal_client("route_a") is first
        assert factories.sepal.call_count == 2


def test_session_info_lists_the_module_clients():
    manager = SessionManager()
    with _stack():
        manager.create_session(module_name="route_a")
        manager.create_session(module_name="route_b")
        info = manager.get_session_info("kernel-a")

    assert info.has_sepal_client is True
    assert info.module_names == ("route_a", "route_b")
    assert info.active_module_name == "route_b"


def test_cleanup_closes_every_module_client():
    manager = SessionManager()
    with _stack():
        manager.create_session(module_name="route_a")
        manager.create_session(module_name="route_b")
        clients = [manager.get_sepal_client("route_a"), manager.get_sepal_client("route_b")]
        manager.cleanup_session("kernel-a")

    for client in clients:
        client.close.assert_called_once()


def test_get_sepal_client_returns_none_without_a_resolvable_scope():
    """A per-connection runtime with no resolvable scope must get None, not an exception.

    Reachable off the render thread -- a background export task, a callback
    on GEEInterface's private loop -- where no kernel context resolves. This
    is get_current_sepal_client()'s documented "returns None" contract, unlike
    get_gee_interface()/get_drive_interface() (and therefore
    get_current_gee_interface()/get_current_drive_interface()), which must
    keep raising.
    """
    manager = SessionManager()
    with _stack():
        with patch.object(
            SessionManager, "get_scope_id", side_effect=sm.UnsupportedSolaraRuntimeError("no scope")
        ):
            assert manager.get_sepal_client() is None


def test_get_sepal_client_returns_none_for_the_reserved_process_scope():
    """The no-argument path must not leak the shared process/dev-auth session's client.

    ``get_sepal_client`` has its own scope resolution, separate from
    ``_require_connection_session`` -- this pins the same reserved-scope
    collision on that path. Unlike ``get_gee_interface``/``get_drive_interface``,
    it never raises here either: it degrades to "no client". A session is
    seeded at ``PROCESS_SCOPE`` so the assertion can't pass by coincidence of
    that key simply being unpopulated.
    """
    manager = SessionManager()
    manager._registry.set(
        {"active_module_name": "route_a", "sepal_clients": {"route_a": MagicMock()}},
        PROCESS_SCOPE,
    )
    with _stack():
        with patch.object(sm, "resolve_scope_id", return_value=PROCESS_SCOPE):
            assert manager.get_sepal_client() is None


def test_get_sepal_client_refuses_an_explicitly_named_process_scope():
    """The ``scope_id`` parameter must not be a second door into the process bucket.

    The test above pins the *resolved* scope. Guarding only that left a caller
    who names ``PROCESS_SCOPE`` outright reading the shared process/dev-auth
    session's client -- the same collision from the other side. No ``_stack()``
    here on purpose: an explicit scope never consults the plan, so nothing about
    this can pass by way of a patched topology.
    """
    manager = SessionManager()
    manager._registry.set(
        {"active_module_name": "route_a", "sepal_clients": {"route_a": MagicMock()}},
        PROCESS_SCOPE,
    )

    assert manager.get_sepal_client(scope_id=PROCESS_SCOPE) is None


def test_get_current_sepal_client_accepts_an_explicit_module():
    from pysepal.solara import utils

    manager = SessionManager()
    with _stack():
        manager.create_session(module_name="route_a")
        manager.create_session(module_name="route_b")

        assert utils.get_current_sepal_client("route_a") is manager.get_sepal_client("route_a")
        assert utils.get_current_sepal_client() is manager.get_sepal_client("route_b")


def test_invalid_connection_headers_raise_instead_of_degrading():
    """A per-connection runtime must never fall through to machine credentials.

    Before v4 a header dict that failed SepalHeaders validation surfaced as a
    bare pydantic ValidationError, which @with_sepal_sessions rendered as
    "An error has occurred" -- indistinguishable from a GEE outage.
    """
    manager = SessionManager()
    with _stack():
        with patch.object(
            sm,
            "SepalHeaders",
            SimpleNamespace(model_validate=MagicMock(side_effect=_validation_error())),
        ):
            with pytest.raises(MissingSepalHeadersError, match="SEPAL authentication headers"):
                manager.create_session()

    assert manager.session_scope_ids() == ()


def test_a_process_runtime_creates_a_session_without_any_headers():
    """Voila, plain Jupyter and scripts own one identity; headers are irrelevant."""
    manager = SessionManager()
    with _stack(raw_headers=None):
        with patch.object(sm, "_current_plan", return_value=_PROCESS_PLAN):
            manager.create_session(module_name="route_a")

    assert sorted(manager.session_scope_ids()) == [PROCESS_SCOPE]
    assert manager._registry.get(PROCESS_SCOPE)["active_module_name"] == "route_a"


def test_the_process_session_builds_nothing_eagerly():
    """One missing credential source must not deny the others.

    A notebook outside a sandbox can resolve GEE credentials while having no
    SEPAL API credentials at all, so components are built one at a time on
    first use rather than all at once in create_session.
    """
    manager = SessionManager()
    with _stack(raw_headers=None) as factories:
        with patch.object(sm, "_current_plan", return_value=_PROCESS_PLAN):
            manager.create_session()

        assert factories.gee.call_count == 0
        assert factories.sepal.call_count == 0
        assert factories.drive.call_count == 0


def test_repeat_process_renders_reuse_one_session():
    manager = SessionManager()
    with _stack(raw_headers=None):
        with patch.object(sm, "_current_plan", return_value=_PROCESS_PLAN):
            manager.create_session(module_name="route_a")
            first = manager._registry.get(PROCESS_SCOPE)
            manager.create_session(module_name="route_b")
            second = manager._registry.get(PROCESS_SCOPE)

    assert first is second
    assert second["active_module_name"] == "route_b"


def test_cleanup_never_tombstones_the_process_scope():
    """Closing a page ends a connection, not the process.

    cleanup_session pops the session and writes a permanent tombstone. Applied
    to the shared process session that would tear down every notebook's
    interfaces and then refuse to rebuild them.
    """
    manager = SessionManager()
    with _stack(raw_headers=None):
        with patch.object(sm, "_current_plan", return_value=_PROCESS_PLAN):
            manager.create_session(module_name="route_a")
            manager.cleanup_session(PROCESS_SCOPE)

            assert PROCESS_SCOPE in manager.session_scope_ids()
            manager.create_session(module_name="route_b")

    assert manager._registry.get(PROCESS_SCOPE)["active_module_name"] == "route_b"


def test_a_new_module_failing_on_a_live_session_leaves_it_intact():
    """Debt 2.3: the reuse-branch SepalClient.create() failure policy.

    An already-live session visiting a new route whose client creation fails
    keeps the session and every other module's client. The exception propagates
    so the route reports the real failure instead of rendering with a client
    that silently points at the wrong module.
    """
    manager = SessionManager()
    with _stack() as factories:
        manager.create_session(module_name="route_a")
        good_client = manager._registry.get("kernel-a")["sepal_clients"]["route_a"]

        factories.sepal.side_effect = RuntimeError("SEPAL API is down")
        with pytest.raises(RuntimeError, match="SEPAL API is down"):
            manager.create_session(module_name="route_b")

        session = manager._registry.get("kernel-a")
        assert session["gee_interface"] is not None
        assert session["sepal_clients"] == {"route_a": good_client}
        assert session["active_module_name"] == "route_a"


def test_headers_without_a_sepal_sessionid_raise_instead_of_a_bare_keyerror():
    """SepalHeaders.parse_cookies silently drops unparsable cookies.

    A structurally valid header set can therefore validate with an empty
    cookie jar. Before this fix that surfaced downstream as a bare
    ``KeyError: 'SEPAL-SESSIONID'`` -- exactly the failure mode this release's
    safety rule exists to eliminate.
    """
    manager = SessionManager()
    with _stack():
        with patch.object(
            sm,
            "SepalHeaders",
            SimpleNamespace(
                model_validate=lambda _v: SimpleNamespace(
                    sepal_user=SimpleNamespace(username="alice"),
                    cookies={},
                    session_id=None,
                )
            ),
        ):
            with pytest.raises(MissingSepalHeadersError, match="SEPAL-SESSIONID"):
                manager.create_session()

    assert manager.session_scope_ids() == ()


def test_dev_auth_headers_without_a_sepal_sessionid_raise():
    """The same empty-cookie-jar failure, reached through the DEV_AUTH process path."""
    manager = SessionManager()
    with _stack(raw_headers=None):
        with patch.object(
            sm, "_current_plan", return_value=SessionPlan(SessionSource.DEV_AUTH, "test")
        ):
            with patch.object(
                sm,
                "prime_dev_auth",
                return_value=SimpleNamespace(
                    sepal_user=SimpleNamespace(username="dev"),
                    cookies={},
                    session_id=None,
                ),
            ):
                with pytest.raises(MissingSepalHeadersError, match="SEPAL-SESSIONID"):
                    manager.create_session()

    assert manager.session_scope_ids() == ()
