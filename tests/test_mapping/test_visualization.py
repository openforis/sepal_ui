"""Tests for SEPAL visualization parameter helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

import ee
import pytest

from pysepal.mapping.visualization import (
    _serialize_viz_value,
    merge_viz_params,
    process_props,
    set_viz_params,
)

# ---------------------------------------------------------------------------
# _serialize_viz_value
# ---------------------------------------------------------------------------


def test_serialize_viz_value_passes_through_scalar_strings():
    assert _serialize_viz_value("name", "default") == "default"
    assert _serialize_viz_value("type", "categorical") == "categorical"


def test_serialize_viz_value_serializes_list_keys_as_comma_separated():
    assert _serialize_viz_value("palette", ["#ff0000", "#00ff00"]) == "#ff0000,#00ff00"
    assert _serialize_viz_value("bands", ["red", "green", "blue"]) == "red,green,blue"
    assert _serialize_viz_value("labels", ["a", "b"]) == "a,b"


def test_serialize_viz_value_normalizes_inverted_to_lowercase_booleans():
    assert _serialize_viz_value("inverted", [True, False, True]) == "true,false,true"


def test_serialize_viz_value_serializes_numeric_lists():
    assert _serialize_viz_value("min", [0, 0, 0]) == "0,0,0"
    assert _serialize_viz_value("max", [255]) == "255"
    assert _serialize_viz_value("values", [1, 30, 40, 50, 51]) == "1,30,40,50,51"


def test_serialize_viz_value_accepts_pre_serialized_strings():
    """Callers may pass an already-comma-separated string for list keys."""
    assert _serialize_viz_value("palette", "#ff0000,#00ff00") == "#ff0000,#00ff00"


# ---------------------------------------------------------------------------
# set_viz_params property shape
# ---------------------------------------------------------------------------


def _fake_image() -> MagicMock:
    """Return a mock that mimics ``ee.Image.set`` returning a new ``ee.Image``."""
    image = MagicMock(spec=ee.Image)
    image.set.return_value = MagicMock(spec=ee.Image)
    return image


def test_set_viz_params_writes_namespaced_properties_for_categorical():
    image = _fake_image()

    result = set_viz_params(
        image,
        name="default",
        type="categorical",
        bands=["classification"],
        palette=["#ffff00", "#8b0000", "#d3d3d3"],
        values=[1, 25, 30],
        labels=["loss 2001", "loss 2025", "non forest"],
    )

    image.set.assert_called_once()
    properties = image.set.call_args[0][0]
    assert properties == {
        "visualization_0_name": "default",
        "visualization_0_type": "categorical",
        "visualization_0_bands": "classification",
        "visualization_0_palette": "#ffff00,#8b0000,#d3d3d3",
        "visualization_0_values": "1,25,30",
        "visualization_0_labels": "loss 2001,loss 2025,non forest",
    }
    assert result is image.set.return_value


def test_set_viz_params_skips_unset_keys():
    image = _fake_image()

    set_viz_params(
        image,
        name="continuous",
        type="continuous",
        bands=["b1"],
        min=0,
        max=1,
    )

    properties = image.set.call_args[0][0]
    assert set(properties.keys()) == {
        "visualization_0_name",
        "visualization_0_type",
        "visualization_0_bands",
        "visualization_0_min",
        "visualization_0_max",
    }
    assert properties["visualization_0_min"] == "0"
    assert properties["visualization_0_max"] == "1"


def test_set_viz_params_supports_multiple_indices():
    image = _fake_image()
    set_viz_params(image, name="alt", type="continuous", bands=["b"], index=2)

    properties = image.set.call_args[0][0]
    assert "visualization_2_name" in properties
    assert "visualization_2_type" in properties
    # No visualization_0_* keys should be written when index=2.
    assert all(key.startswith("visualization_2_") for key in properties)


def test_set_viz_params_returns_image_unchanged_when_no_kwargs_given():
    image = _fake_image()
    result = set_viz_params(image, name=None, type=None)  # type: ignore[arg-type]
    # No properties to write — return the input image as-is.
    image.set.assert_not_called()
    assert result is image


def test_set_viz_params_rejects_non_image_inputs():
    with pytest.raises(TypeError, match=r"ee\.Image"):
        set_viz_params("not an image", name="default")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Roundtrip with process_props (the read path that SepalMap uses on display)
# ---------------------------------------------------------------------------


def test_set_viz_params_roundtrips_through_process_props_categorical():
    """The properties emitted by set_viz_params should parse back via process_props."""
    image = _fake_image()
    set_viz_params(
        image,
        name="loss_year",
        type="categorical",
        bands=["classification"],
        palette=["#ffff00", "#8b0000", "#d3d3d3"],
        values=[1, 25, 30],
        labels=["loss 2001", "loss 2025", "non forest"],
    )

    written = image.set.call_args[0][0]
    parsed = process_props(written, props={})

    assert parsed == {
        "0": {
            "name": "loss_year",
            "type": "categorical",
            "bands": ["classification"],
            "palette": ["#ffff00", "#8b0000", "#d3d3d3"],
            "values": [1, 25, 30],
            "labels": ["loss 2001", "loss 2025", "non forest"],
        }
    }


def test_set_viz_params_roundtrips_through_process_props_continuous():
    image = _fake_image()
    set_viz_params(
        image,
        name="elevation",
        type="continuous",
        bands=["elevation"],
        min=0,
        max=3000,
        palette=["#0000ff", "#00ff00", "#ff0000"],
    )

    written = image.set.call_args[0][0]
    parsed = process_props(written, props={})

    assert parsed["0"]["name"] == "elevation"
    assert parsed["0"]["type"] == "continuous"
    assert parsed["0"]["bands"] == ["elevation"]
    assert parsed["0"]["min"] == [0.0]
    assert parsed["0"]["max"] == [3000.0]
    assert parsed["0"]["palette"] == ["#0000ff", "#00ff00", "#ff0000"]


def test_set_viz_params_roundtrips_inverted_flags():
    image = _fake_image()
    set_viz_params(
        image,
        name="rgb",
        type="rgb",
        bands=["r", "g", "b"],
        min=[0, 0, 0],
        max=[1, 1, 1],
        inverted=[True, False, False],
    )

    written = image.set.call_args[0][0]
    parsed = process_props(written, props={})

    assert parsed["0"]["inverted"] == [True, False, False]


# ---------------------------------------------------------------------------
# merge_viz_params
# ---------------------------------------------------------------------------


def test_merge_viz_params_last_value_wins():
    base = {"palette": ["#000"], "min": 0, "max": 255}
    override = {"max": 100}
    merged = merge_viz_params(base, override)
    assert merged == {"palette": ["#000"], "min": 0, "max": 100}


def test_merge_viz_params_ignores_none_values():
    merged = merge_viz_params(
        {"palette": ["#000"]},
        {"palette": None, "min": 0},
    )
    assert merged == {"palette": ["#000"], "min": 0}


def test_merge_viz_params_handles_empty_inputs():
    assert merge_viz_params() == {}
    assert merge_viz_params({}, None) == {}  # type: ignore[arg-type]
