"""SepalClient.create() is pure; the directory POST never runs on a render."""

import threading
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
from pysepal_api import SepalClient as RealSepalClient

from pysepal.solara import session_manager as sm
from pysepal.solara._topology import SessionPlan, SessionSource
from pysepal.solara.runtime_context import PROCESS_SCOPE
from pysepal.solara.session_manager import SessionManager

_PROCESS = SessionPlan(SessionSource.PROCESS, "test")


class _ImmediateExecutor:
    """Runs submitted work inline so the test can assert on its effect."""

    def __init__(self):
        self.submitted = 0

    def submit(self, fn, *args, **kwargs):
        self.submitted += 1
        fn(*args, **kwargs)


def _client():
    return SimpleNamespace(ensure_results_dir=MagicMock(), module_name="route_a")


def test_creating_a_client_does_not_touch_the_network_on_the_render_path():
    manager = SessionManager()
    client = _client()
    executor = _ImmediateExecutor()

    with (
        patch.object(sm, "_current_plan", return_value=_PROCESS),
        patch.object(sm, "is_sepal_sandbox", return_value=True),
        patch.object(sm, "SepalClient", SimpleNamespace(create=MagicMock(return_value=client))),
        patch.object(sm, "_RESULTS_DIR_EXECUTOR", executor),
    ):
        manager.create_session(module_name="route_a")
        assert client.ensure_results_dir.call_count == 0

        manager.get_sepal_client()

    assert executor.submitted == 1
    assert client.ensure_results_dir.call_count == 1


def test_the_directory_is_scheduled_once_per_module():
    """Exercises ``_schedule_results_dir``'s own dedup guard directly.

    The client cache already prevents re-scheduling from the render path, so
    callers only ever invoke this once per client and would never reach the
    guard on their own.
    """
    manager = SessionManager()
    client = _client()
    executor = _ImmediateExecutor()
    session = {"results_dirs_scheduled": set()}

    with patch.object(sm, "_RESULTS_DIR_EXECUTOR", executor):
        manager._schedule_results_dir(session, "route_a", client)
        manager._schedule_results_dir(session, "route_a", client)
        manager._schedule_results_dir(session, "route_a", client)

    assert executor.submitted == 1


def test_a_rejected_submission_does_not_mark_the_module_scheduled():
    """A submit() failure must not be mistaken for a scheduled directory.

    It must not escape onto the render path either, and must stay eligible
    for a later attempt.
    """
    manager = SessionManager()
    client = _client()
    executor = SimpleNamespace(
        submit=MagicMock(side_effect=RuntimeError("executor is shutting down"))
    )
    session = {"results_dirs_scheduled": set()}

    with patch.object(sm, "_RESULTS_DIR_EXECUTOR", executor):
        manager._schedule_results_dir(session, "route_a", client)  # must not raise

    assert "route_a" not in session["results_dirs_scheduled"]


def test_a_failing_directory_creation_does_not_break_the_session():
    manager = SessionManager()
    client = _client()
    client.ensure_results_dir.side_effect = RuntimeError("SEPAL API is down")
    executor = _ImmediateExecutor()

    with (
        patch.object(sm, "_current_plan", return_value=_PROCESS),
        patch.object(sm, "is_sepal_sandbox", return_value=True),
        patch.object(sm, "SepalClient", SimpleNamespace(create=MagicMock(return_value=client))),
        patch.object(sm, "_RESULTS_DIR_EXECUTOR", executor),
    ):
        manager.create_session(module_name="route_a")
        assert manager.get_sepal_client() is client

    assert manager._sessions[PROCESS_SCOPE]["sepal_clients"]["route_a"] is client


def test_the_process_gee_interface_refuses_a_shared_service_account():
    """The credential-reading call site states its intent explicitly.

    The one place pysepal may read ~/.config/earthengine/credentials.
    """
    from_default = MagicMock(return_value=MagicMock())
    manager = SessionManager()

    with (
        patch.object(sm, "_current_plan", return_value=_PROCESS),
        patch.object(sm, "EESession", SimpleNamespace(from_default=from_default)),
        patch.object(sm, "GEEInterface", MagicMock(side_effect=lambda *_a, **_k: MagicMock())),
    ):
        manager.get_gee_interface()

    assert from_default.call_args.kwargs == {"allow_service_account_file": False}


def test_the_drive_interface_is_closed_without_a_version_sniff():
    """ee-client 4.0 gives every credential holder close(); no getattr probe."""
    import inspect

    source = inspect.getsource(SessionManager._close_session)

    assert 'getattr(session.get("drive_interface")' not in source
    assert 'session["drive_interface"].close()' in source


def test_the_results_dir_post_never_happens_on_the_render_thread():
    """Instruments httpx.Client.send() directly, with a real SepalClient.

    The tests above mock ``SepalClient`` entirely, which proves the manager
    *schedules* work but cannot prove that work stays off the render thread
    once a real client issues a real request: a mock can't accidentally make
    a network call, so it can't fail this way. Here the client is the actual
    ``pysepal-api`` one; only ``auth``/``base_url`` are pinned so construction
    can't fall back to reading real files or hitting a real host. Any
    ``send()`` observed on the thread that called into the manager fails the
    test immediately -- from inside the render call itself, not after the
    fact.
    """
    render_thread = threading.current_thread()
    calls = []

    def _instrumented_send(self, request, **kwargs):
        if threading.current_thread() is render_thread:
            raise AssertionError(
                f"HTTP request issued on the render thread: {request.method} {request.url}"
            )
        calls.append(request)
        return httpx.Response(200, request=request, json={})

    def _real_client(**kwargs):
        return RealSepalClient.create(
            module_name=kwargs.get("module_name"),
            auth=httpx.BasicAuth("test", "test"),
            base_url="https://sepal.example",
        )

    manager = SessionManager()
    futures = []
    real_submit = sm._RESULTS_DIR_EXECUTOR.submit

    def _spy_submit(fn, *args, **kwargs):
        future = real_submit(fn, *args, **kwargs)
        futures.append(future)
        return future

    with (
        patch.object(httpx.Client, "send", _instrumented_send),
        patch.object(sm, "_current_plan", return_value=_PROCESS),
        patch.object(sm, "is_sepal_sandbox", return_value=True),
        patch.object(sm, "SepalClient", SimpleNamespace(create=_real_client)),
        patch.object(sm._RESULTS_DIR_EXECUTOR, "submit", side_effect=_spy_submit),
    ):
        manager.create_session(module_name="route_a")
        manager.get_sepal_client()

        # Wait for the background thread *inside* the patch scope: submit() only
        # schedules the work and returns, so the worker can still be running
        # ensure_results_dir() well after this block would otherwise have
        # unpatched httpx.Client.send and let it fall through to a real request.
        assert len(futures) == 1
        # Block until the worker finishes: submit() returns before it starts, so
        # httpx.Client.send must stay patched until the request is done.
        futures[0].result(timeout=5)

    assert len(calls) == 1
    assert calls[0].method == "POST"
    assert calls[0].url.path == "/api/user-files/createFolder"
