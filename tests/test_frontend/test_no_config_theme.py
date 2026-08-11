"""The theme no longer round-trips through ~/.sepal-ui-config (issue #977)."""

import ipyvuetify as v
import pytest

import pysepal
import pysepal.scripts.utils as su
from pysepal.frontend import styles


def test_get_theme_is_gone():
    assert not hasattr(styles, "get_theme")
    assert not hasattr(pysepal, "get_theme")


def test_dark_theme_default_is_a_constant():
    """A class-body trait default read from $HOME pinned one user's theme process-wide."""
    assert styles.SepalColor._dark_theme.default_value is True


def test_set_colors_writes_nothing(tmp_path, monkeypatch):
    """No write anywhere -- not just not at $HOME.

    ``pysepal.conf`` binds ``config_file`` once at import time, so patching
    ``$HOME`` can't retarget it: the writer resolves the name through
    ``pysepal.scripts.utils`` (its own ``from pysepal.conf import
    config_file``), so that is the name that must be patched to actually
    observe a write.
    """
    fake_config_file = tmp_path / ".sepal-ui-config"
    monkeypatch.setattr(su, "config_file", fake_config_file)
    color = styles.SepalColor()
    color._dark_theme = False
    color.set_colors()
    assert not fake_config_file.exists()


def test_set_colors_still_tracks_the_live_vuetify_theme():
    color = styles.SepalColor()
    v.theme.dark = True
    assert color.theme_name == "dark"
    v.theme.dark = False
    assert color.theme_name == "light"


def test_theme_select_writes_nothing(tmp_path, monkeypatch):
    """Same fix as ``test_set_colors_writes_nothing``: patch the bound name, not $HOME."""
    from pysepal import sepalwidgets as sw

    fake_config_file = tmp_path / ".sepal-ui-config"
    monkeypatch.setattr(su, "config_file", fake_config_file)
    select = sw.ThemeSelect()
    select.toggle_theme()
    assert not fake_config_file.exists()


def test_module_theme_entry_point_is_gone():
    with pytest.raises(ModuleNotFoundError):
        __import__("pysepal.bin.module_theme")
