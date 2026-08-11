"""Names pysepal 4.0 retired. Re-introducing any of them is a regression.

Module absence is asserted against *this* checkout rather than with a bare
``ImportError``. A developer machine often has another pysepal on the path --
an editable install of a sibling clone, say -- and a retired module resolving
out of that one says nothing about what this tree ships. Anchoring on
``REPO_ROOT`` keeps the guard answering the only question worth asking.
"""

import importlib
import importlib.util
from pathlib import Path

import pytest

import pysepal

REPO_ROOT = Path(__file__).parents[1]

RETIRED_MODULES = [
    "sepal_ui",
    "pysepal.conf",
    "pysepal.scripts.sepal_client",
    "pysepal.bin.module_theme",
    "pysepal.bin.module_l10n",
]

RETIRED_ATTRIBUTES = [
    ("pysepal", "config"),
    ("pysepal", "config_file"),
    ("pysepal", "get_theme"),
    ("pysepal.frontend.styles", "get_theme"),
    ("pysepal.scripts.utils", "set_config"),
    ("pysepal.scripts.utils", "_write_config"),
    ("pysepal.scripts.utils", "set_config_locale"),
    ("pysepal.scripts.utils", "set_config_theme"),
    ("pysepal.solara.session_manager", "empty_session_info"),
    ("pysepal.solara.session_manager", "can_create_sessions"),
    ("pysepal.solara.session_manager", "reset_dev_headers_cache"),
    ("pysepal.solara.utils", "_fallback_gee_interface"),
    ("pysepal.solara.utils", "_fallback_drive_interface"),
    ("pysepal.solara.runtime_context", "get_current_runtime_id"),
    ("pysepal.solara.notifications.bus", "_get_kernel_id"),
]

RETIRED_METHODS = [
    ("pysepal.solara.session_manager", "SessionManager", "get_kernel_id"),
    ("pysepal.solara.session_manager", "SessionManager", "get_session_component"),
    ("pysepal.solara.session_manager", "SessionManager", "list_sessions"),
]


def _origin(module: str) -> Path | None:
    """Return where ``module`` would be imported from, or None if nowhere.

    Args:
        module: Dotted module name to resolve without importing it.

    Returns:
        The resolved source path, or ``None`` when the name does not resolve
        or resolves to something without a file (a namespace package).
    """
    try:
        spec = importlib.util.find_spec(module)
    except (ImportError, AttributeError, ValueError):
        return None
    return Path(spec.origin) if spec is not None and spec.origin else None


def test_the_package_under_test_is_this_checkout():
    """Anchors every assertion below; without it they could all be vacuous."""
    assert Path(pysepal.__file__).is_relative_to(REPO_ROOT)


@pytest.mark.parametrize("module", RETIRED_MODULES)
def test_retired_modules_are_not_shipped(module):
    origin = _origin(module)
    assert origin is None or not origin.is_relative_to(REPO_ROOT), origin


@pytest.mark.parametrize(("module", "name"), RETIRED_ATTRIBUTES)
def test_retired_attributes_are_gone(module, name):
    assert not hasattr(importlib.import_module(module), name)


@pytest.mark.parametrize(("module", "cls", "name"), RETIRED_METHODS)
def test_retired_methods_are_gone(module, cls, name):
    assert not hasattr(getattr(importlib.import_module(module), cls), name)
