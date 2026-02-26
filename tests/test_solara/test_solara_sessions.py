"""Tests for Solara session initialization behavior."""

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

import sepal_ui.solara.decorators as decorators_module
import sepal_ui.solara.session_manager as session_manager_module
from sepal_ui.solara.session_manager import SessionManager


@pytest.fixture(autouse=True)
def reset_session_manager_singleton():
    """Reset SessionManager singleton state between tests."""
    SessionManager._instance = None
    SessionManager._sessions = {}
    yield
    SessionManager._instance = None
    SessionManager._sessions = {}


def test_create_session_raises_for_invalid_headers(monkeypatch):
    """Malformed header payloads should raise to expose contract issues."""
    monkeypatch.setenv("SOLARA_TEST", "false")
    monkeypatch.setattr(SessionManager, "get_kernel_id", lambda _: "kernel-1")
    monkeypatch.setattr(
        session_manager_module,
        "headers",
        SimpleNamespace(value={"host": ["0.0.0.0:8765"]}),
    )

    manager = SessionManager()
    with pytest.raises(ValidationError):
        manager.create_session(module_name="test")


def test_create_session_is_idempotent_for_same_kernel(monkeypatch):
    """Calling create_session twice should keep the existing session."""
    monkeypatch.setenv("SOLARA_TEST", "false")
    monkeypatch.setattr(SessionManager, "get_kernel_id", lambda _: "kernel-2")
    monkeypatch.setattr(
        session_manager_module,
        "headers",
        SimpleNamespace(value={"any": ["header"]}),
    )

    validate_calls = {"count": 0}

    def fake_validate(_):
        validate_calls["count"] += 1
        return SimpleNamespace(
            sepal_user=SimpleNamespace(username="alice"),
            cookies={"SEPAL-SESSIONID": "session-id"},
        )

    monkeypatch.setattr(
        session_manager_module.SepalHeaders,
        "model_validate",
        staticmethod(fake_validate),
    )
    monkeypatch.setattr(session_manager_module, "EESession", lambda sepal_headers: sepal_headers)
    monkeypatch.setattr(session_manager_module, "GEEInterface", lambda gee_session: gee_session)
    monkeypatch.setattr(
        session_manager_module,
        "SepalClient",
        lambda session_id, module_name: (session_id, module_name),
    )
    monkeypatch.setattr(
        session_manager_module,
        "GDriveInterface",
        lambda sepal_headers: sepal_headers,
    )

    manager = SessionManager()
    first_ready = manager.create_session(module_name="test-module")
    second_ready = manager.create_session(module_name="test-module")

    assert first_ready is True
    assert second_ready is True
    assert validate_calls["count"] == 1
    assert manager.get_session_component("username") == "alice"


def test_with_sepal_sessions_waits_until_session_ready(monkeypatch):
    """Decorator should render waiting state when session manager is not ready yet."""
    monkeypatch.setattr(
        decorators_module,
        "headers",
        SimpleNamespace(value={"host": ["0.0.0.0:8765"]}),
    )

    info_messages = []
    monkeypatch.setattr(
        decorators_module.solara,
        "Info",
        lambda message: info_messages.append(message),
    )

    class DummySessionManager:
        def create_session(self, module_name="default"):
            return False

    monkeypatch.setattr(decorators_module, "SessionManager", DummySessionManager)

    component_called = {"value": False}

    @decorators_module.with_sepal_sessions(waiting_message="auth pending")
    def page():
        component_called["value"] = True
        return "ready"

    result = page()

    assert result is None
    assert component_called["value"] is False
    assert info_messages == ["auth pending"]


def test_with_sepal_sessions_runs_component_when_ready(monkeypatch):
    """Decorator should execute the wrapped component once session is ready."""
    monkeypatch.setattr(
        decorators_module,
        "headers",
        SimpleNamespace(value={"host": ["0.0.0.0:8765"]}),
    )
    monkeypatch.setattr(decorators_module.solara, "Info", lambda *_: None)

    class DummySessionManager:
        def create_session(self, module_name="default"):
            return True

    monkeypatch.setattr(decorators_module, "SessionManager", DummySessionManager)

    @decorators_module.with_sepal_sessions(waiting_message="auth pending")
    def page():
        return "ready"

    assert page() == "ready"
