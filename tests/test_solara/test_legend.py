"""Tests for the reusable Solara map legend dataclasses."""

from dataclasses import asdict

from pysepal.solara.components.legend import DiscreteEntry, LegendData


def test_discrete_entry_detail_defaults_empty():
    entry = DiscreteEntry(label="Forest", color="#006400")
    assert entry.detail == ""


def test_discrete_entry_detail_roundtrips_through_asdict():
    entry = DiscreteEntry(label="Nival", color="#ff0000", detail="1,234 km² · 12%")
    assert asdict(entry) == {
        "label": "Nival",
        "color": "#ff0000",
        "detail": "1,234 km² · 12%",
    }


def test_legend_data_serializes_items_with_detail_and_empty_color():
    data = LegendData(items=[DiscreteEntry("Total", "", detail="9,999 km² · 100%")])
    payload = asdict(data)
    assert payload["items"][0]["color"] == ""
    assert payload["items"][0]["detail"] == "9,999 km² · 100%"
    assert payload["gradients"] == []
