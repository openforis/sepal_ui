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
        items=[DiscreteEntry("Forest", "#006400")],
    )
    LegendComponent(legend_data=asdict(legend))
"""

from dataclasses import dataclass, field


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


@dataclass
class LegendData:
    """Complete legend specification passed to LegendComponent."""

    gradients: list[GradientEntry] = field(default_factory=list)
    items: list[DiscreteEntry] = field(default_factory=list)
