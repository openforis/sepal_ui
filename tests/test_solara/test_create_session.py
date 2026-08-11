"""Tests for SessionManager.create_session hardening (locking, identity, tombstone)."""

import threading
import time
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pysepal.solara import session_manager as sm
from pysepal.solara.errors import MissingSepalHeadersError, SessionScopeClosedError
from pysepal.solara.session_manager import SessionManager

_MISSING = object()


def _parsed_headers(username="alice", session_id="sid-1"):
    return SimpleNamespace(
        sepal_user=SimpleNamespace(username=username),
        cookies={"SEPAL-SESSIONID": session_id},
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
    sepal_factory = MagicMock(side_effect=lambda **kwargs: MagicMock())
    drive_factory = MagicMock(side_effect=lambda **kwargs: MagicMock())

    with (
        patch.object(sm, "resolve_scope_id", return_value="kernel-a"),
        patch.object(sm, "headers", SimpleNamespace(value=header_value)),
        patch.object(sm, "SepalHeaders", SimpleNamespace(model_validate=lambda _v: parsed)),
        patch.object(sm, "EESession", SimpleNamespace(from_sepal_headers=lambda _h: MagicMock())),
        patch.object(sm, "GEEInterface", gee_factory),
        patch.object(sm, "SepalClient", SimpleNamespace(create=sepal_factory)),
        patch.object(sm, "GDriveInterface", drive_factory),
    ):
        yield SimpleNamespace(gee=gee_factory, sepal=sepal_factory, drive=drive_factory)


def test_typed_accessors_replace_the_string_keyed_getter():
    """No public accessor may take a session-dict key as a string."""
    manager = SessionManager()
    assert not hasattr(manager, "get_session_component")
    with _stack():
        manager.create_session(module_name="route_a")
        assert manager.get_gee_interface() is manager._sessions["kernel-a"]["gee_interface"]
        assert manager.get_drive_interface() is manager._sessions["kernel-a"]["drive_interface"]
        assert manager.get_sepal_client("route_a") is not None


def test_typed_accessors_return_none_without_a_session():
    """Superseded in F4, which makes the per-connection miss raise instead."""
    manager = SessionManager()
    with _stack():
        assert manager.get_gee_interface() is None
        assert manager.get_drive_interface() is None


def test_missing_headers_raise_instead_of_returning_silently():
    manager = SessionManager()
    with _stack(raw_headers=None):
        with pytest.raises(MissingSepalHeadersError, match="kernel-a"):
            manager.create_session()

    assert manager.list_sessions() == {}


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
        assert manager.list_sessions()["kernel-a"]["raw_headers"] is sm.headers.value


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
    assert manager.get_session_info("kernel-a")["username"] == "bob"


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

    assert "kernel-a" not in manager._sessions
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
        assert manager.list_sessions() == {}


def test_cleanup_closes_a_drive_interface_that_has_close():
    """ee-client 4.0.0 gives GDriveInterface a close(); cleanup must use it."""
    manager = SessionManager()
    with _stack() as factories:
        manager.create_session()
        drive = manager.get_drive_interface()
        manager.cleanup_session("kernel-a")

    assert factories.drive.call_count == 1
    drive.close.assert_called_once()


def test_cleanup_tolerates_a_drive_interface_without_close(caplog):
    """On ee-client 3.0.0 GDriveInterface has no close(); that must not raise -- or log.

    A ``getattr(..., "close", None)`` skip and a ``close()`` call caught by the
    surrounding ``except Exception`` would both leave ``list_sessions()`` empty,
    so that assertion alone can't tell them apart. Asserting on the log record
    is what actually proves the skip path ran instead of the catch path.
    """
    manager = SessionManager()
    with _stack() as factories:
        factories.drive.side_effect = lambda **kwargs: SimpleNamespace()
        manager.create_session()
        with caplog.at_level("ERROR", logger="sepalui.session_manager"):
            manager.cleanup_session("kernel-a")

    assert manager.list_sessions() == {}
    assert "Error closing Drive interface" not in caplog.text


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

    assert info["has_sepal_client"] is True
    assert info["module_names"] == ["route_a", "route_b"]
    assert info["active_module_name"] == "route_b"


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
    """A runtime with no resolvable scope must get None, not an exception.

    This is the documented get_current_sepal_client() behaviour change (PR
    body): it never raises UnsupportedSolaraRuntimeError, unlike
    get_gee_interface()/get_drive_interface() (and therefore
    get_current_gee_interface()/get_current_drive_interface()), which must
    keep raising.
    """
    manager = SessionManager()
    with patch.object(
        SessionManager, "get_scope_id", side_effect=sm.UnsupportedSolaraRuntimeError("no scope")
    ):
        assert manager.get_sepal_client() is None


def test_get_current_sepal_client_accepts_an_explicit_module():
    from pysepal.solara import utils

    manager = SessionManager()
    with _stack():
        manager.create_session(module_name="route_a")
        manager.create_session(module_name="route_b")

        assert utils.get_current_sepal_client("route_a") is manager.get_sepal_client("route_a")
        assert utils.get_current_sepal_client() is manager.get_sepal_client("route_b")


def test_dev_login_happens_once_per_process(monkeypatch):
    """get_sepal_headers_from_auth is a blocking POST on the render path."""
    monkeypatch.setenv("SOLARA_TEST", "true")
    logins = []
    parsed = _parsed_headers()

    def _login():
        logins.append(1)
        return parsed

    monkeypatch.setattr(sm, "get_sepal_headers_from_auth", _login)

    manager = SessionManager()
    with _stack():
        manager.create_session()
        manager.cleanup_session("kernel-a")

    assert sm.resolve_sepal_headers({"cookie": ["y"]}) is parsed
    assert logins == [1]
