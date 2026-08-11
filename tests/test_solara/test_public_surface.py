"""pysepal.solara has one public surface, and it is complete."""

import ast
from pathlib import Path

import pysepal.solara as ps

INIT_PATH = Path(ps.__file__)


def test_errors_are_reachable_from_the_package_root():
    for name in (
        "SepalSessionError",
        "MissingSepalHeadersError",
        "SessionScopeClosedError",
        "UnsupportedSolaraRuntimeError",
    ):
        assert name in ps.__all__
        assert getattr(ps, name) is not None


def test_scope_helpers_are_reachable_from_the_package_root():
    for name in ("PROCESS_SCOPE", "current_scope_id", "resolve_scope_id"):
        assert name in ps.__all__


def test_the_topology_types_stay_private():
    """Exporting the enum in a major freezes its members; no app touches it."""
    for name in ("SessionSource", "SessionPlan", "resolve_session_plan"):
        assert name not in ps.__all__


def test_all_is_sorted_and_every_entry_resolves():
    assert ps.__all__ == sorted(ps.__all__)
    for name in ps.__all__:
        assert hasattr(ps, name), name


def test_every_name_imported_into_the_package_is_declared_public():
    """Catch the other half of a surface bug.

    A name reachable off ``ps`` but missing from ``__all__`` -- e.g. via
    ``from .x import a, b`` where only ``a`` was added to ``__all__`` --
    would slip past ``hasattr``, which only checks that declared names
    resolve, not that resolvable names are declared.
    """
    tree = ast.parse(INIT_PATH.read_text())
    imported_names = {
        alias.asname or alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
        if not (alias.asname or alias.name).startswith("_")
    }
    assert imported_names == set(ps.__all__)


def test_docstring_does_not_say_sepal_ui():
    assert "sepal_ui" not in ps.__doc__
