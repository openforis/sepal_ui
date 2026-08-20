"""Names pysepal 4.0 retired. Re-introducing any of them is a regression.

Module absence is asserted against *this* checkout rather than with a bare
``ImportError`` -- see ``tests._import_probe`` for why the interpreter at large
is the wrong thing to ask.
"""

import importlib
from pathlib import Path

import pytest

import pysepal
from tests._import_probe import REPO_ROOT, shipped_locations

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


def test_the_package_under_test_is_this_checkout():
    """Anchors every assertion below; without it they could all be vacuous."""
    assert Path(pysepal.__file__).is_relative_to(REPO_ROOT)


@pytest.mark.parametrize("module", RETIRED_MODULES)
def test_retired_modules_are_not_shipped(module):
    shipped = shipped_locations(module)
    assert shipped == [], shipped


@pytest.mark.parametrize(("module", "name"), RETIRED_ATTRIBUTES)
def test_retired_attributes_are_gone(module, name):
    assert not hasattr(importlib.import_module(module), name)


@pytest.mark.parametrize(("module", "cls", "name"), RETIRED_METHODS)
def test_retired_methods_are_gone(module, cls, name):
    assert not hasattr(getattr(importlib.import_module(module), cls), name)
