"""The theme no longer round-trips through ~/.sepal-ui-config (issue #977)."""

from pathlib import Path

import ipyvuetify as v
import pytest

import pysepal
from pysepal.frontend import styles


def test_get_theme_is_gone():
    assert not hasattr(styles, "get_theme")
    assert not hasattr(pysepal, "get_theme")


def test_dark_theme_default_is_a_constant():
    """A class-body trait default read from $HOME pinned one user's theme process-wide."""
    assert styles.SepalColor._dark_theme.default_value is True


def test_set_colors_writes_nothing(tmp_path, monkeypatch):
    """No write anywhere -- not just not at $HOME.

    ``pysepal.conf`` and its config-writer plumbing are gone (issue #977), so
    there is no bound name left to patch -- patching ``$HOME`` is enough now.
    """
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    color = styles.SepalColor()
    color._dark_theme = False
    color.set_colors()
    assert list(tmp_path.iterdir()) == []


def test_set_colors_still_tracks_the_live_vuetify_theme():
    color = styles.SepalColor()
    v.theme.dark = True
    assert color.theme_name == "dark"
    v.theme.dark = False
    assert color.theme_name == "light"


def test_theme_select_writes_nothing(tmp_path, monkeypatch):
    """Same invariant as ``test_set_colors_writes_nothing``."""
    from pysepal import sepalwidgets as sw

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    select = sw.ThemeSelect()
    select.toggle_theme()
    assert list(tmp_path.iterdir()) == []


def test_module_theme_entry_point_is_gone():
    with pytest.raises(ModuleNotFoundError):
        __import__("pysepal.bin.module_theme")
