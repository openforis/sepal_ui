"""Tests for the typed dataclass models used by MapAppComponent."""

import pytest

from pysepal.solara.components.layout import (
    ExternalLink,
    PanelSection,
    RightPanelConfig,
    StepAction,
    StepConfig,
)


def test_step_config_defaults():
    step = StepConfig(id=1, name="AOI")
    assert step.id == 1
    assert step.name == "AOI"
    assert step.icon == "mdi-checkbox-blank-circle-outline"
    assert step.display == "step"
    assert step.right_panel_action is None
    assert step.content is None
    assert step.content_enabled is True
    assert step.actions == ()
    assert step.width is None
    assert step.height is None


def test_step_config_is_frozen():
    step = StepConfig(id=1, name="A")
    with pytest.raises(Exception):
        step.id = 2  # type: ignore[misc]


def test_step_config_rejects_invalid_display():
    with pytest.raises(ValueError):
        StepConfig(id=1, name="A", display="window")  # type: ignore[arg-type]


def test_step_config_rejects_invalid_right_panel_action():
    with pytest.raises(ValueError):
        StepConfig(id=1, name="A", right_panel_action="flip")  # type: ignore[arg-type]


def test_step_action_defaults():
    action = StepAction(label="OK", event="confirm")
    assert action.cancel is False


def test_panel_section_defaults():
    section = PanelSection(title="Layers")
    assert section.icon == ""
    assert section.divider is False
    assert section.description == ""
    assert callable(section.content)


def test_right_panel_config_defaults():
    cfg = RightPanelConfig()
    assert cfg.title == "Tools"
    assert cfg.icon == "mdi-widgets"
    assert cfg.width == 300
    assert cfg.description == ""
    assert cfg.toggle_icon == "mdi-chevron-left"


def test_external_link_defaults():
    link = ExternalLink(title="Docs", url="https://example.org")
    assert link.icon == "mdi-open-in-new"
