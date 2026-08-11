"""Tests for the @with_sepal_sessions gate."""

import inspect
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import solara

from pysepal.solara import session_manager as sm
from pysepal.solara._topology import SessionPlan, SessionSource
from pysepal.solara.decorators import with_sepal_sessions
from pysepal.solara.errors import MissingSepalHeadersError

_PER_CONNECTION = SessionPlan(SessionSource.PER_CONNECTION, "test")
_PROCESS = SessionPlan(SessionSource.PROCESS, "test")


def test_the_header_gate_parameters_are_gone():
    """show_loading/waiting_message existed only to paper over Voila."""
    parameters = inspect.signature(with_sepal_sessions).parameters

    assert list(parameters) == ["module_name", "error_handler"]


def test_a_per_connection_render_without_headers_reports_instead_of_waiting():
    """The old gate rendered a spinner forever; the error must now surface."""
    errors = []

    @solara.component
    @with_sepal_sessions(module_name="route_a", error_handler=errors.append)
    def Page():
        solara.Text("rendered")

    with (
        patch.object(sm, "_current_plan", return_value=_PER_CONNECTION),
        patch.object(sm, "headers", SimpleNamespace(value=None)),
        patch.object(sm.SessionManager, "get_scope_id", return_value="kernel-a"),
    ):
        box, _ = solara.render(Page(), handle_error=False)

    assert [type(e) for e in errors] == [MissingSepalHeadersError]
    assert box.children[0].children == []


def test_a_process_render_needs_no_headers_at_all():
    """Voila, plain Jupyter and scripts must render, not wait."""
    rendered = []

    @solara.component
    @with_sepal_sessions(module_name="route_a")
    def Page():
        rendered.append(True)
        solara.Text("rendered")

    with (
        patch.object(sm, "_current_plan", return_value=_PROCESS),
        patch.object(sm, "headers", SimpleNamespace(value=None)),
    ):
        solara.render(Page(), handle_error=False)

    assert rendered == [True]


def test_the_component_runs_once_the_session_exists():
    rendered = []

    @solara.component
    @with_sepal_sessions(module_name="route_a")
    def Page():
        rendered.append(True)
        solara.Text("rendered")

    create = MagicMock()
    with (
        patch.object(sm, "_current_plan", return_value=_PER_CONNECTION),
        patch.object(sm.SessionManager, "create_session", create),
    ):
        solara.render(Page(), handle_error=False)

    assert rendered == [True]
    assert create.call_args.kwargs == {"module_name": "route_a"}
