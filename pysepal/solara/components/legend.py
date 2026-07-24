"""Reusable floating map legend for Solara apps.

Supports discrete color chips and continuous gradient bars.
Designed for bottom-center overlay on map-based pysepal apps.

Usage:
    from pysepal.solara.components.legend import (
        LegendComponent, LegendData, GradientEntry, DiscreteEntry,
    )
    from dataclasses import asdict

    legend = LegendData(
        gradients=[GradientEntry(colors=["#ffff00", "#8b0000"], labels=["2001", "2024"])],
        items=[DiscreteEntry("Forest", "#006400", detail="12,345 km² · 42%")],
    )
    LegendComponent(legend_data=asdict(legend))
"""

from dataclasses import dataclass, field
from typing import Callable, Optional

import solara


@dataclass
class GradientEntry:
    """A continuous color ramp with labeled endpoints."""

    colors: list[str]
    labels: list[str]
    title: str = ""


@dataclass
class DiscreteEntry:
    """A single labeled color chip."""

    label: str
    color: str
    detail: str = ""


@dataclass
class LegendData:
    """Complete legend specification passed to LegendComponent."""

    gradients: list[GradientEntry] = field(default_factory=list)
    items: list[DiscreteEntry] = field(default_factory=list)


@solara.component_vue("Legend.vue")
def LegendComponent(
    legend_data: Optional[dict] = None,
    visible: bool = True,
    collapsed: bool = False,
    event_set_collapsed: Optional[Callable[[bool], None]] = None,
    selector_options: Optional[list] = None,
    selected: Optional[str] = None,
    event_set_selected: Optional[Callable[[str], None]] = None,
):
    """Floating map legend overlay.

    Renders at bottom-center of the viewport over the map area.
    Supports gradient bars and discrete color chips.

    Args:
        legend_data: Serialized LegendData (use dataclasses.asdict).
            Empty dict or missing keys = nothing rendered.
        visible: Show/hide the entire legend.
        collapsed: Collapsed state (icon pill only).
        event_set_collapsed: Callback when user toggles collapse.
        selector_options: Optional [{"value", "text"}] layer options. When two
            or more are given, a compact dropdown renders at the top of the
            legend body; one or none renders no dropdown.
        selected: The currently selected option value.
        event_set_selected: Callback when the user picks a different option.
    """
    pass
