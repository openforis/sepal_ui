"""Tests for SEPAL visualization parameter helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

import ee
import pytest

from pysepal.mapping.visualization import (
    merge_viz_params,
    process_props,
    set_viz_params,
)


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

    set_viz_params(image, name="continuous", type="continuous", bands=["b1"], min=0, max=1)

    properties = image.set.call_args[0][0]
    assert set(properties.keys()) == {
        "visualization_0_name",
        "visualization_0_type",
        "visualization_0_bands",
        "visualization_0_min",
        "visualization_0_max",
    }


def test_set_viz_params_supports_multiple_indices():
    image = _fake_image()
    set_viz_params(image, name="alt", type="continuous", bands=["b"], index=2)

    properties = image.set.call_args[0][0]
    assert all(key.startswith("visualization_2_") for key in properties)


def test_set_viz_params_rejects_non_image_inputs():
    with pytest.raises(TypeError, match=r"ee\.Image"):
        set_viz_params("not an image", name="default")  # type: ignore[arg-type]


# The roundtrips against process_props are the load-bearing checks: they
# guarantee SepalMap can read back exactly what set_viz_params writes.


def test_set_viz_params_roundtrips_through_process_props_categorical():
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

    parsed = process_props(image.set.call_args[0][0], props={})

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

    parsed = process_props(image.set.call_args[0][0], props={})

    assert parsed["0"]["type"] == "continuous"
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

    parsed = process_props(image.set.call_args[0][0], props={})

    assert parsed["0"]["inverted"] == [True, False, False]


def test_merge_viz_params_last_value_wins_and_drops_nones():
    merged = merge_viz_params(
        {"palette": ["#000"], "min": 0, "max": 255},
        {"max": 100, "palette": None},
    )
    assert merged == {"palette": ["#000"], "min": 0, "max": 100}
