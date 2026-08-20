"""Paths used by the application.

A real module keeps user files in the SEPAL workspace through ``SepalClient``;
this local path only seeds the AOI file picker with the repo's test fixtures so
the demo has something to open out of the box.
"""

from pathlib import Path

DUMMY_DATA_DIR = Path(__file__).resolve().parents[6] / "tests" / "data" / "aoi_manual"
