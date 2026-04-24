"""Meta-tests guarding test-infrastructure configuration."""

from pathlib import Path

import pytest
import tomli as tomllib


@pytest.fixture(scope="session")
def pyproject(root_dir: Path) -> dict:
    """Load pyproject.toml as a dict."""
    with open(root_dir / "pyproject.toml", "rb") as f:
        return tomllib.load(f)


def test_pytest_markers_registered(pyproject: dict) -> None:
    """Both `unit` and `gee` markers must be registered."""
    markers = pyproject["tool"]["pytest"]["ini_options"]["markers"]
    joined = " ".join(markers)
    assert "gee:" in joined, "gee marker missing from pyproject.toml"
    assert "unit:" in joined, "unit marker missing from pyproject.toml"


def test_pytest_default_excludes_gee(pyproject: dict) -> None:
    """Default pytest invocation must deselect gee-marked tests."""
    addopts = pyproject["tool"]["pytest"]["ini_options"]["addopts"]
    assert "not gee" in addopts, "addopts must contain -m 'not gee' to keep local dev fast"
