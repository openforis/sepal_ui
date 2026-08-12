"""Test the ThemeSelect widget."""

import pytest

from pysepal import sepalwidgets as sw


def test_init(theme_select: sw.ThemeSelect) -> None:
    """Check Init widget.

    Args:
        theme_select: a widget instance removing all existing config
    """
    # minimal btn
    assert isinstance(theme_select, sw.ThemeSelect)

    return


def test_change_theme(theme_select: sw.ThemeSelect) -> None:
    """The widget owns its own dark trait; nothing is persisted."""
    before = theme_select.dark
    theme_select.toggle_theme()
    assert theme_select.dark is not before


@pytest.fixture(scope="function")
def theme_select() -> sw.ThemeSelect:
    """Create a simple theme_select.

    Returns:
        the object instance
    """
    return sw.ThemeSelect()
