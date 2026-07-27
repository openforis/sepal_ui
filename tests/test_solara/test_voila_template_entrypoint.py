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
