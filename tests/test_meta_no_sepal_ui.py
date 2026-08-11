"""The sepal_ui compatibility package is gone in pysepal 4.0.

Absence is asserted against *this* checkout -- see ``tests._import_probe`` for
why the interpreter at large is the wrong thing to ask.
"""

import subprocess
import sys

from tests._import_probe import REPO_ROOT, defined_in_repo, shipped_locations


def test_sepal_ui_is_not_shipped():
    """Named for what it checks: another clone on the path may still import."""
    shipped = shipped_locations("sepal_ui")
    assert shipped == [], shipped


def test_no_meta_path_finder_is_installed():
    """The shim inserted a MetaPathFinder at sys.meta_path[0]; this tree may not.

    Matching on the class name would both miss a finder that came back under a
    new one and go red for a foreign finder imported from some other clone on
    the path. What settles it is whether the code defining the finder lives in
    this checkout.
    """
    ours = [type(finder).__name__ for finder in sys.meta_path if defined_in_repo(finder)]
    assert ours == []


def test_the_package_directory_is_gone():
    assert not (REPO_ROOT / "sepal_ui").exists()


def test_importing_pysepal_emits_no_rename_deprecation():
    code = (
        "import warnings; "
        "warnings.filterwarnings('error', message=\".*'sepal_ui' package is deprecated.*\"); "
        "import pysepal"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
