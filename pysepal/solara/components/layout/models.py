"""Typed dataclass props for MapAppComponent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal, Optional, Tuple

DisplayMode = Literal["step", "dialog"]
RightPanelAction = Literal["open", "close", "toggle"]


def _noop() -> None:
    """Default render callable for empty content slots."""
    return None


@dataclass(frozen=True)
class StepAction:
    """Button shown in a step's dialog footer."""

    label: str
    event: str
    cancel: bool = False


@dataclass(frozen=True)
class StepConfig:
    """A single entry in the MapApp left-drawer step list."""

    id: int
    name: str
    icon: str = "mdi-checkbox-blank-circle-outline"
    display: DisplayMode = "step"
    right_panel_action: Optional[RightPanelAction] = None
    content: Optional[Callable[[], None]] = None
    content_enabled: bool = True
    actions: Tuple[StepAction, ...] = ()
    width: Optional[int] = None
    height: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate enum-like fields at construction time."""
        if self.display not in ("step", "dialog"):
            raise ValueError(f"StepConfig.display must be 'step' or 'dialog', got {self.display!r}")
        if self.right_panel_action is not None and self.right_panel_action not in (
            "open",
            "close",
            "toggle",
        ):
            raise ValueError(
                "StepConfig.right_panel_action must be one of open/close/toggle, "
                f"got {self.right_panel_action!r}"
            )


@dataclass(frozen=True)
class PanelSection:
    """A section rendered inside the right panel."""

    title: str
    icon: str = ""
    content: Callable[[], None] = field(default=_noop)
    divider: bool = False
    description: str = ""


@dataclass(frozen=True)
class RightPanelConfig:
    """Display configuration for the right panel."""

    title: str = "Tools"
    icon: str = "mdi-widgets"
    width: int = 300
    description: str = ""
    toggle_icon: str = "mdi-chevron-left"


@dataclass(frozen=True)
class ExternalLink:
    """An external link tile shown in the drawer's bottom section."""

    title: str
    url: str
    icon: str = "mdi-open-in-new"
