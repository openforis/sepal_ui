"""Floating map legend driven by the layers currently on the map."""

from dataclasses import asdict

import solara

from pysepal.solara.components.legend import LegendComponent


@solara.component
def MapLegend(layer_legends):
    """Float the legend of the selected layer bottom-center over the map.

    The dropdown appears once two or more layers publish a legend; a single
    layer renders its legend on its own.
    """
    selected_legend = solara.use_reactive("")

    legends = layer_legends.value
    current_legend = next(
        (entry for entry in legends if entry.layer_id == selected_legend.value), None
    )
    # Falling back to the first entry is not cosmetic: the legend only renders
    # while it has gradients or items, so an unmatched selection would take the
    # layer dropdown down with it and leave no way back.
    current_legend = current_legend or (legends[0] if legends else None)

    LegendComponent(
        legend_data=asdict(current_legend.data) if current_legend else {},
        selector_options=[{"value": entry.layer_id, "text": entry.label} for entry in legends],
        selected=current_legend.layer_id if current_legend else "",
        event_set_selected=selected_legend.set,
    )
