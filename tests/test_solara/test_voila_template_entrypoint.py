"""Structural checks for the thin Voila template entrypoint."""

from __future__ import annotations

import ast
import json
from pathlib import Path

TEMPLATE_DIR = (
    Path(__file__).resolve().parents[2] / "pysepal" / "templates" / "solara" / "solara_map_app"
)
APP_PATH = TEMPLATE_DIR / "app.py"
NOTEBOOK_PATH = TEMPLATE_DIR / "ui.ipynb"
TEMPLATE_SOURCES = sorted(TEMPLATE_DIR.rglob("*.py"))


def _decorator_name(decorator: ast.expr) -> str:
    if isinstance(decorator, ast.Call):
        return _decorator_name(decorator.func)
    if isinstance(decorator, ast.Attribute):
        return decorator.attr
    if isinstance(decorator, ast.Name):
        return decorator.id
    return ""


def test_app_exposes_shared_component_and_authenticated_page_wrapper():
    """The Solara page authenticates before delegating to shared UI code."""
    module = ast.parse(APP_PATH.read_text())
    functions = {
        node.name: node
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    shared = functions["MapAppDemo"]
    page = functions["Page"]

    assert [_decorator_name(item) for item in shared.decorator_list] == ["component"]
    assert [_decorator_name(item) for item in page.decorator_list] == [
        "component",
        "with_sepal_sessions",
    ]
    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "MapAppDemo"
        for statement in page.body
        for node in ast.walk(statement)
    )


def test_app_is_only_the_shell():
    """Logic belongs under ``component/``; ``app.py`` only opens and lays out the app.

    Guards the module boundaries against the template drifting back into one file.
    """
    module = ast.parse(APP_PATH.read_text())

    defined = {
        node.name
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }

    assert defined == {"on_kernel_start", "MapAppDemo", "Page"}


def test_template_never_schedules_gee_work_on_a_second_event_loop():
    """Every async button must go through solara's loop, not GEEInterface's own.

    ``GEEInterface.create_task`` hands the coroutine to a private event loop running
    in its own thread, while ``solara.lab.use_task`` runs it on solara's. Mixing both
    in one app makes two loops share the single ``httpx.AsyncClient(http2=True)``
    cached on the eeclient session, and its asyncio primitives bind to whichever loop
    touched them first -- so a concurrent call from the other one dies mid-request.
    """
    offenders = [
        path.relative_to(TEMPLATE_DIR)
        for path in TEMPLATE_SOURCES
        for node in ast.walk(ast.parse(path.read_text()))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "create_task"
    ]

    assert offenders == []


def test_voila_notebook_only_imports_and_displays_shared_component():
    """The notebook remains a thin runtime entrypoint with no duplicated UI."""
    notebook = json.loads(NOTEBOOK_PATH.read_text())

    assert len(notebook["cells"]) == 1
    cell = notebook["cells"][0]
    source = "".join(cell["source"])

    assert cell["cell_type"] == "code"
    assert source == ("from app import MapAppDemo\n" "\n" "display(MapAppDemo())\n")
    assert not any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        for node in ast.walk(ast.parse(source))
    )
