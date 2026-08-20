"""Data produced by one processing run."""

from dataclasses import dataclass

import ee


@dataclass(frozen=True, slots=True)
class ProcessingOutputs:
    """Earth Engine objects produced by one processing run."""

    pixel_area: ee.Image
    elevation_class: ee.Image
    multi_band: ee.Image
    region: ee.Geometry
    name_prefix: str
