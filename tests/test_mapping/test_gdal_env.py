"""Test the GDAL/PROJ data environment sanitizer."""

import os
import sys

from pysepal.mapping.gdal_env import prune_foreign_gdal_env


def test_prune_foreign_gdal_env(monkeypatch) -> None:
    """Foreign GDAL/PROJ data paths are pruned, own-prefix paths are kept."""
    # foreign paths (e.g. the SEPAL system GDAL) are removed
    monkeypatch.setenv("GDAL_DATA", "/nonexistent-foreign/share/gdal")
    monkeypatch.setenv("PROJ_LIB", "/nonexistent-foreign/share/proj")
    prune_foreign_gdal_env()
    assert "GDAL_DATA" not in os.environ
    assert "PROJ_LIB" not in os.environ

    # paths inside sys.prefix (the environment's own GDAL stack) are kept
    own_gdal = os.path.join(sys.prefix, "share", "gdal")
    own_proj = os.path.join(sys.prefix, "share", "proj")
    monkeypatch.setenv("GDAL_DATA", own_gdal)
    monkeypatch.setenv("PROJ_LIB", own_proj)
    prune_foreign_gdal_env()
    assert os.environ["GDAL_DATA"] == own_gdal
    assert os.environ["PROJ_LIB"] == own_proj

    # unset variables are left untouched
    monkeypatch.delenv("GDAL_DATA", raising=False)
    monkeypatch.delenv("PROJ_LIB", raising=False)
    prune_foreign_gdal_env()
    assert "GDAL_DATA" not in os.environ
    assert "PROJ_LIB" not in os.environ
