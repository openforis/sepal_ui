"""Tests for process-scoped sessions: the runtimes that own exactly one identity."""

import threading
import time
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from pysepal_api.errors import NoCredentialsError, ServerError

from pysepal.solara import session_manager as sm
from pysepal.solara._topology import SessionPlan, SessionSource
from pysepal.solara.errors import SepalSessionError
from pysepal.solara.runtime_context import PROCESS_SCOPE
from pysepal.solara.session_manager import SessionManager

_PROCESS = SessionPlan(SessionSource.PROCESS, "test")
_DEV_AUTH = SessionPlan(SessionSource.DEV_AUTH, "test")
_PER_CONNECTION = SessionPlan(SessionSource.PER_CONNECTION, "test")


def _dev_headers(username="alice"):
    return SimpleNamespace(
        sepal_user=SimpleNamespace(username=username),
        cookies={"SEPAL-SESSIONID": "sid-1"},
        session_id="sid-1",
    )


@contextmanager
def _process_stack(plan=_PROCESS, dev_headers=None, sandbox=True, gee_delay=0.0):
    """Patch every constructor a process session can reach for."""
    from_default = MagicMock(side_effect=lambda **kwargs: MagicMock())
    from_sepal_headers = MagicMock(side_effect=lambda _h: MagicMock())

    def _build_gee(*_args, **_kwargs):
        if gee_delay:
            time.sleep(gee_delay)
        return MagicMock()

    gee_factory = MagicMock(side_effect=_build_gee)
    drive_factory = MagicMock(side_effect=lambda **kwargs: MagicMock())
    sepal_factory = MagicMock(
        side_effect=lambda **kwargs: SimpleNamespace(
            ensure_results_dir=MagicMock(), module_name=kwargs.get("module_name")
        )
    )

    with (
        patch.object(sm, "_current_plan", return_value=plan),
        patch.object(sm, "is_sepal_sandbox", return_value=sandbox),
        patch.object(
            sm,
            "EESession",
            SimpleNamespace(from_default=from_default, from_sepal_headers=from_sepal_headers),
        ),
        patch.object(sm, "GEEInterface", gee_factory),
        patch.object(sm, "GDriveInterface", drive_factory),
        patch.object(sm, "SepalClient", SimpleNamespace(create=sepal_factory)),
        patch.object(sm, "prime_dev_auth", MagicMock(return_value=dev_headers)),
        patch.object(sm, "_RESULTS_DIR_EXECUTOR", SimpleNamespace(submit=lambda fn: fn())),
    ):
        yield SimpleNamespace(
            from_default=from_default,
            from_sepal_headers=from_sepal_headers,
            gee=gee_factory,
            drive=drive_factory,
            sepal=sepal_factory,
        )


def test_the_process_shares_one_gee_interface():
    """Two interfaces means two private event loops, one of them orphaned."""
    manager = SessionManager()
    with _process_stack() as factories:
        first = manager.get_gee_interface()
        second = manager.get_gee_interface()

    assert first is second
    assert factories.from_default.call_count == 1
    assert factories.gee.call_count == 1


def test_concurrent_first_renders_build_one_process_gee_interface():
    """Two GEEInterfaces means two private event loops, one of them orphaned.

    The PER_CONNECTION analog of this race is a canary
    (``test_concurrent_first_renders_build_one_gee_interface``); the PROCESS
    path shares the same lazy-build shape and needs the same coverage.
    """
    manager = SessionManager()
    start = threading.Barrier(4)

    with _process_stack(gee_delay=0.05) as factories:

        def _worker():
            start.wait()
            manager.get_gee_interface()

        threads = [threading.Thread(target=_worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert factories.gee.call_count == 1


def test_the_process_session_is_keyed_at_the_process_scope():
    manager = SessionManager()
    with _process_stack():
        manager.get_gee_interface()

    assert sorted(manager._sessions) == [PROCESS_SCOPE]


def test_asking_for_gee_does_not_build_drive_or_a_client():
    manager = SessionManager()
    with _process_stack() as factories:
        manager.get_gee_interface()

        assert factories.drive.call_count == 0
        assert factories.sepal.call_count == 0


def test_the_process_shares_one_drive_interface():
    manager = SessionManager()
    with _process_stack() as factories:
        assert manager.get_drive_interface() is manager.get_drive_interface()
        assert factories.drive.call_count == 1
        assert factories.drive.call_args.kwargs == {}


def test_no_sepal_client_outside_a_sandbox():
    """A notebook or script outside SEPAL keeps writing to the local filesystem.

    Building a client here would silently move every `if sepal_client:` branch
    in the deployed apps from local paths to the SEPAL API.
    """
    manager = SessionManager()
    with _process_stack(sandbox=False) as factories:
        assert manager.get_sepal_client() is None
        assert factories.sepal.call_count == 0
        assert manager.get_gee_interface() is not None


def test_a_sandbox_client_is_none_without_sepal_api_credentials():
    manager = SessionManager()
    with _process_stack() as factories:
        factories.sepal.side_effect = NoCredentialsError("no key")

        assert manager.get_sepal_client() is None
        assert manager.get_gee_interface() is not None


def test_a_sandbox_client_is_none_on_a_sepal_api_outage():
    """A PysepalError out of SepalClient.create() (e.g. an unreachable auth source).

    Must degrade the sandbox path to "no client" -- exactly like missing
    credentials -- not escape and turn an export dialog render into an error
    banner instead of the local-filesystem fallback it exists to preserve.
    """
    manager = SessionManager()
    with _process_stack() as factories:
        factories.sepal.side_effect = ServerError(503, url="http://sepal/api", body="boom")

        assert manager.get_sepal_client() is None
        assert manager.get_gee_interface() is not None


def test_each_module_gets_its_own_process_client():
    manager = SessionManager()
    with _process_stack() as factories:
        manager.create_session(module_name="route_a")
        client_a = manager.get_sepal_client()
        manager.create_session(module_name="route_b")
        client_b = manager.get_sepal_client()

    assert client_a is not client_b
    assert factories.sepal.call_count == 2
    assert [call.kwargs["module_name"] for call in factories.sepal.call_args_list] == [
        "route_a",
        "route_b",
    ]


def test_a_sandbox_client_authenticates_from_the_sandbox_file():
    """No SEPAL headers on the process session means the sandbox key, not a session cookie."""
    manager = SessionManager()
    with _process_stack() as factories:
        manager.create_session(module_name="route_a")
        manager.get_sepal_client()

    assert factories.sepal.call_args.kwargs["auth_mode"] == "sandbox_file"


def test_revisiting_a_process_module_reuses_its_client():
    """Switching the active module alone must not build a client for it.

    Unlike the per-connection path, ``create_session`` on the process path
    only moves ``active_module_name``; a client is built solely by
    ``get_sepal_client``, which route_b's leg here never calls.
    """
    manager = SessionManager()
    with _process_stack() as factories:
        manager.create_session(module_name="route_a")
        first = manager.get_sepal_client()
        manager.create_session(module_name="route_b")
        manager.create_session(module_name="route_a")

        assert manager.get_sepal_client() is first
        assert factories.sepal.call_count == 1


def test_dev_auth_builds_the_process_session_from_the_developer_login():
    """Machine credentials must not be touched when a developer login is in use."""
    manager = SessionManager()
    with _process_stack(plan=_DEV_AUTH, dev_headers=_dev_headers(), sandbox=False) as factories:
        manager.get_gee_interface()
        manager.get_drive_interface()

        assert factories.from_sepal_headers.call_count == 1
        assert factories.from_default.call_count == 0
        assert factories.drive.call_args.kwargs["sepal_headers"] is not None
        assert manager._sessions[PROCESS_SCOPE]["username"] == "alice"


def test_dev_auth_clients_carry_the_developer_session_id():
    manager = SessionManager()
    with _process_stack(plan=_DEV_AUTH, dev_headers=_dev_headers(), sandbox=False) as factories:
        manager.create_session(module_name="route_a")
        manager.get_sepal_client()

    assert factories.sepal.call_args.kwargs["session_id"] == "sid-1"
    assert factories.sepal.call_args.kwargs["auth_mode"] == "auto"


def test_per_connection_accessors_raise_without_a_session():
    """No decorator, no session: that is a bug in the app, not a fallback case."""
    manager = SessionManager()
    with _process_stack(plan=_PER_CONNECTION):
        with patch.object(SessionManager, "get_scope_id", return_value="kernel-a"):
            with pytest.raises(SepalSessionError, match="with_sepal_sessions"):
                manager.get_gee_interface()
            with pytest.raises(SepalSessionError, match="with_sepal_sessions"):
                manager.get_drive_interface()
            assert manager.get_sepal_client() is None


def test_per_connection_accessors_refuse_the_reserved_process_scope():
    """Solara's kernel id is client-supplied; ``process`` is not allowlisted.

    A connection that lands on scope id ``PROCESS_SCOPE`` (deliberately or by
    accident, e.g. ``?kernelid=process``) must not read or write the shared
    process/dev-auth session through the per-connection path.
    """
    manager = SessionManager()
    with _process_stack(plan=_PER_CONNECTION):
        with patch.object(SessionManager, "get_scope_id", return_value=PROCESS_SCOPE):
            with pytest.raises(SepalSessionError, match="reserved process scope"):
                manager.get_gee_interface()
            with pytest.raises(SepalSessionError, match="reserved process scope"):
                manager.get_drive_interface()


def test_closing_the_process_session_releases_it_and_allows_a_rebuild():
    """The process session's lifetime is the process; teardown is explicit.

    cleanup_session refuses the process scope, so this is the only way to
    release it -- embedders and tests need it, nothing else calls it.
    """
    manager = SessionManager()
    with _process_stack() as factories:
        first = manager.get_gee_interface()
        manager.close_process_session()

        assert PROCESS_SCOPE not in manager._sessions
        second = manager.get_gee_interface()

    assert second is not first
    assert factories.gee.call_count == 2


def test_close_does_not_orphan_a_concurrent_build():
    """A close racing an in-flight build must not detach a live interface.

    ``get_gee_interface`` used to ensure the session shell and build the
    interface under two separate lock acquisitions; a concurrent
    ``close_process_session`` landing in the gap between them could pop the
    session dict while the accessor still held a reference to it, so the
    in-flight build wrote a live ``GEEInterface`` into a dict no longer
    reachable from ``_sessions`` -- a leaked interface (private event loop)
    that nothing would ever close. The fix serialises ensure-and-build under
    one lock acquisition, so close must now block until the build finishes.
    """
    manager = SessionManager()
    build_started = threading.Event()
    release_build = threading.Event()
    built_interface = MagicMock()
    calls = []

    def _slow_gee(*_a, **_k):
        if not calls:
            calls.append(1)
            build_started.set()
            release_build.wait(timeout=5.0)
            return built_interface
        return MagicMock()

    result = {}

    def _call():
        result["interface"] = manager.get_gee_interface()

    with _process_stack() as factories:
        factories.gee.side_effect = _slow_gee

        build_thread = threading.Thread(target=_call)
        build_thread.start()
        assert build_started.wait(timeout=2.0)

        close_thread = threading.Thread(target=manager.close_process_session)
        close_thread.start()
        close_thread.join(timeout=0.2)
        assert close_thread.is_alive(), "close_process_session must block on the still-held lock"

        release_build.set()
        build_thread.join(timeout=2.0)
        close_thread.join(timeout=2.0)
        assert not build_thread.is_alive()
        assert not close_thread.is_alive()

        assert result["interface"] is built_interface
        assert PROCESS_SCOPE not in manager._sessions
        built_interface.close.assert_called_once()

        rebuilt = manager.get_gee_interface()
        assert rebuilt is not built_interface


@pytest.mark.parametrize(
    "accessor", ["get_gee_interface", "get_drive_interface", "get_sepal_client"]
)
def test_process_accessors_take_the_scope_lock_once(accessor):
    """A second acquisition is a gap a concurrent close_process_session slips into.

    Staging the race with a slow component constructor cannot pin this: that
    constructor runs inside the second acquisition in the buggy code too, so
    close merely blocks on the lock and every timing-based assertion still
    holds. The invariant that actually rules the gap out is structural: ensure
    and build must happen under exactly one lock acquisition, not two.
    """
    manager = SessionManager()
    taken = []
    real_scope_lock = SessionManager._scope_lock

    def counting(self, scope_id):
        taken.append(scope_id)
        return real_scope_lock(self, scope_id)

    with _process_stack():
        with patch.object(SessionManager, "_scope_lock", counting):
            getattr(manager, accessor)()

    assert taken.count(PROCESS_SCOPE) == 1


def test_a_sandbox_served_app_gets_a_real_interface_not_the_misdirecting_error():
    """F3 alone leaves a SEPAL-sandbox app with an empty session shell.

    ``utils.get_current_gee_interface()`` -- what apps actually call -- used
    to raise "Ensure your Page component is decorated with
    @with_sepal_sessions" here, which is the wrong diagnosis: the real cause
    was that the process path built nothing at all. It must now build the
    session lazily, exactly as a direct ``SessionManager`` call does, and
    never reach that error or the headerless fallback.
    """
    from pysepal.solara import utils

    manager = SessionManager()
    assert SessionManager.is_initialized()

    with _process_stack() as factories:
        interface = utils.get_current_gee_interface()

    assert interface is manager._sessions[PROCESS_SCOPE]["gee_interface"]
    assert factories.gee.call_count == 1
