"""Test the GDAL/PROJ data environment sanitizer."""

import os
import sys
from pathlib import Path

import pytest

from pysepal.mapping.gdal_env import GDAL_ENV_VARS, prune_foreign_gdal_env


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Start every case from an environment with no data variables set."""
    for var in GDAL_ENV_VARS:
        monkeypatch.delenv(var, raising=False)

    return


def test_every_data_var_is_covered() -> None:
    """The cases below parametrize over the constant, so pin what it must hold."""
    assert set(GDAL_ENV_VARS) == {"GDAL_DATA", "PROJ_LIB", "PROJ_DATA"}

    return


@pytest.mark.parametrize("var", GDAL_ENV_VARS)
def test_foreign_path_is_pruned(monkeypatch: pytest.MonkeyPatch, var: str) -> None:
    """A path outside every own prefix belongs to the SEPAL system GDAL."""
    monkeypatch.setenv(var, "/usr/share/gdal")
    prune_foreign_gdal_env()

    assert var not in os.environ

    return


@pytest.mark.parametrize("var", GDAL_ENV_VARS)
def test_own_prefix_path_is_kept(monkeypatch: pytest.MonkeyPatch, var: str) -> None:
    """A path under sys.prefix belongs to this environment's own GDAL stack."""
    own = str(Path(sys.prefix) / "share" / "gdal")
    monkeypatch.setenv(var, own)
    prune_foreign_gdal_env()

    assert os.environ[var] == own

    return


@pytest.mark.parametrize("var", GDAL_ENV_VARS)
def test_base_prefix_path_is_kept(monkeypatch: pytest.MonkeyPatch, var: str) -> None:
    """A venv layered on conda reaches its GDAL stack through sys.base_prefix."""
    own = str(Path(sys.base_prefix) / "share" / "gdal")
    monkeypatch.setattr(sys, "prefix", "/nonexistent/venv")
    monkeypatch.setenv(var, own)
    prune_foreign_gdal_env()

    assert os.environ[var] == own

    return


def test_sibling_prefix_is_pruned(monkeypatch: pytest.MonkeyPatch) -> None:
    """A sibling env sharing a name prefix is foreign, so string matching won't do."""
    monkeypatch.setenv("GDAL_DATA", f"{sys.prefix}-other/share/gdal")
    prune_foreign_gdal_env()

    assert "GDAL_DATA" not in os.environ

    return


def test_empty_value_is_pruned(monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty value sends GDAL looking in an empty directory."""
    monkeypatch.setenv("GDAL_DATA", "")
    prune_foreign_gdal_env()

    assert "GDAL_DATA" not in os.environ

    return


def test_unset_vars_are_left_alone() -> None:
    """The sanitizer is a no-op when the environment exports nothing."""
    prune_foreign_gdal_env()

    assert not any(var in os.environ for var in GDAL_ENV_VARS)

    return
