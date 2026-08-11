"""The sepal_ui compatibility package is gone in pysepal 4.0."""

import subprocess
import sys
from pathlib import Path

import pytest


def test_importing_sepal_ui_fails():
    with pytest.raises(ModuleNotFoundError):
        __import__("sepal_ui")


def test_no_meta_path_finder_is_installed():
    """The shim inserted a MetaPathFinder at sys.meta_path[0]; nothing may now."""
    names = [type(finder).__name__ for finder in sys.meta_path]
    assert "_SepalUiFinder" not in names


def test_the_package_directory_is_gone():
    assert not (Path(__file__).parents[1] / "sepal_ui").exists()


def test_importing_pysepal_emits_no_rename_deprecation():
    code = (
        "import warnings; "
        "warnings.filterwarnings('error', message=\".*'sepal_ui' package is deprecated.*\"); "
        "import pysepal"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
