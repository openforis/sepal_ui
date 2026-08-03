"""Legend state held by the application."""

from dataclasses import dataclass

from pysepal.solara.components.legend import LegendData


@dataclass(frozen=True, slots=True)
class LayerLegend:
    """A map layer paired with the legend shown when it is selected."""

    layer_id: str
    label: str
    data: LegendData
