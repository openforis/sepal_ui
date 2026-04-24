# Phase 2 Rename Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rename the Python package from `sepal_ui`/`sepal-ui` to `pysepal`, maintaining backward compatibility via an import shim.

**Architecture:** Three sequential PRs: (B1) directory rename + packaging + shim, (B2) internal import rename, (B3) notebooks + templates + docs. Each PR builds on the previous and keeps the repo in a testable state.

**Tech Stack:** Python packaging (setuptools), importlib (MetaPathFinder for shim), nox, sphinx, pytest, GitHub Actions CI.

---

## PR B1: Directory Rename + Packaging + Shim

### Task 1: Rename source directory

**Files:**

- Rename: `sepal_ui/` -> `pysepal/`

**Step 1: Rename the directory with git**

Run: `git mv sepal_ui pysepal`

This preserves git history for the renamed files.

**Step 2: Verify the rename**

Run: `ls pysepal/__init__.py`
Expected: file exists

**Step 3: Commit**

```bash
git add -A
git commit -m "refactor: rename sepal_ui/ directory to pysepal/"
```

---

### Task 2: Create the backward-compatibility shim

**Files:**

- Create: `sepal_ui/__init__.py`

**Step 1: Write the shim module**

Create `sepal_ui/__init__.py`:

```python
"""Backward-compatibility shim: redirects all sepal_ui imports to pysepal.

This package is deprecated. Use ``import pysepal`` instead.
"""

import importlib
import importlib.abc
import sys
import warnings

warnings.warn(
    (
        "The 'sepal_ui' package is deprecated and has been renamed to 'pysepal'. "
        "Please update your imports: 'import pysepal' / 'from pysepal import ...'."
    ),
    DeprecationWarning,
    stacklevel=2,
)


class _SepalUiFinder(importlib.abc.MetaPathFinder):
    """Redirect ``sepal_ui.*`` imports to ``pysepal.*``."""

    def find_module(self, fullname, path=None):
        if fullname == "sepal_ui" or fullname.startswith("sepal_ui."):
            return self
        return None

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        new_name = fullname.replace("sepal_ui", "pysepal", 1)
        mod = importlib.import_module(new_name)
        sys.modules[fullname] = mod
        return mod


sys.meta_path.insert(0, _SepalUiFinder())

# Eagerly load pysepal so that top-level attributes are available
import pysepal as _pysepal  # noqa: E402

# Re-export top-level public API
config = _pysepal.config
config_file = _pysepal.config_file
color = _pysepal.color
get_theme = _pysepal.get_theme
SepalColor = _pysepal.SepalColor
__version__ = _pysepal.__version__
__author__ = _pysepal.__author__
__email__ = _pysepal.__email__
```

**Step 2: Verify shim can be imported**

Run: `cd /tmp && python -c "import sepal_ui; print(sepal_ui.__version__)" 2>&1`
Expected: prints the version with a DeprecationWarning

Run: `cd /tmp && python -c "from sepal_ui.mapping import SepalMap; print(SepalMap)" 2>&1`
Expected: prints the class with a DeprecationWarning

**Step 3: Commit**

```bash
git add sepal_ui/__init__.py
git commit -m "feat: add sepal_ui backward-compatibility import shim"
```

---

### Task 3: Update pyproject.toml

**Files:**

- Modify: `pyproject.toml`

**Step 1: Update distribution name (line 6)**

```
- name = "sepal-ui"
+ name = "pysepal"
```

**Step 2: Update entry points (lines 109-116)**

```
- module_deploy = "sepal_ui.bin.module_deploy:main"
- module_factory = "sepal_ui.bin.module_factory:main"
- module_l10n = "sepal_ui.bin.module_l10n:main"
- module_theme = "sepal_ui.bin.module_theme:main"
- module_venv = "sepal_ui.bin.module_venv:main"
- activate_venv = "sepal_ui.bin.activate_venv:main"
- sepal_ipyvuetify = "sepal_ui.bin.sepal_ipyvuetify:main"
- entry_point = "sepal_ui.bin.entry_point:main"
+ module_deploy = "pysepal.bin.module_deploy:main"
+ module_factory = "pysepal.bin.module_factory:main"
+ module_l10n = "pysepal.bin.module_l10n:main"
+ module_theme = "pysepal.bin.module_theme:main"
+ module_venv = "pysepal.bin.module_venv:main"
+ activate_venv = "pysepal.bin.activate_venv:main"
+ sepal_ipyvuetify = "pysepal.bin.sepal_ipyvuetify:main"
+ entry_point = "pysepal.bin.entry_point:main"
```

**Step 3: Update setuptools packages.find (lines 122-124)**

```
- include = ["sepal_ui*"]
+ include = ["pysepal*", "sepal_ui*"]
```

Note: both `pysepal` and `sepal_ui` (the shim) need to be included.

**Step 4: Update package-data (lines 126-135)**

```
- [tool.setuptools.package-data]
- sepal_ui = [
+ [tool.setuptools.package-data]
+ pysepal = [
```

The data paths inside the list stay the same (they're relative to the package root).

**Step 5: Update commitizen version_files (line 145)**

```
-     "sepal_ui/__init__.py:__version__"
+     "pysepal/__init__.py:__version__"
```

**Step 6: Update coverage source and omit (lines 177-183)**

```
- source = ["sepal_ui"]
+ source = ["pysepal"]
  omit = [
-     "sepal_ui/*/__init__.py",
-     "sepal_ui/scripts/messages.py",
-     "sepal_ui/reclassify/parameters.py",
+     "pysepal/*/__init__.py",
+     "pysepal/scripts/messages.py",
+     "pysepal/reclassify/parameters.py",
  ]
```

**Step 7: Update codespell skip (line 193)**

```
- skip = 'CHANGELOG.md,sepal_ui/message/**/*.json,sepal_ui/data/gaul_iso.json'
+ skip = 'CHANGELOG.md,pysepal/message/**/*.json,pysepal/data/gaul_iso.json'
```

**Step 8: Commit**

```bash
git add pyproject.toml
git commit -m "build: update pyproject.toml for pysepal package name"
```

---

### Task 4: Update pysepal/**init**.py

**Files:**

- Modify: `pysepal/__init__.py`

**Step 1: Update module docstring and imports**

The file currently has `from sepal_ui.conf` imports and a deprecation warning for the old package. Update it to be the canonical `pysepal` init:

```python
"""Wrapper for ipyvuetify widgets to unify the display of voila dashboards in the SEPAL platform.

``pysepal`` is a lib designed to create elegant python based dashboard in the SEPAL environment. It is designed on top of the amazing ``ipyvuetify`` library and will help developer to easily create interface for their workflows. By using this libraries, you'll ensure a robust and unified interface for your scripts and a easy and complete integration into the SEPAL dashboard of application.
"""

from pysepal.conf import config as config
from pysepal.conf import config_file as config_file
from pysepal.frontend.styles import SepalColor
from pysepal.frontend.styles import get_theme as get_theme

__author__ = """Pierrick Rambaud"""
__email__ = "pierrick.rambaud49@gmail.com"
__version__ = "3.2.0"

color = SepalColor()
'color: the colors of sepal. members are in the following list: "main, darker, bg, primary, accent, secondary, success, info, warning, error, menu". They will render according to the selected theme.'
```

Note: the deprecation warning is REMOVED from `pysepal/__init__.py` — the shim handles it now.

**Step 2: Commit**

```bash
git add pysepal/__init__.py
git commit -m "refactor: update pysepal/__init__.py imports and remove old deprecation warning"
```

---

### Task 5: Update noxfile.py

**Files:**

- Modify: `noxfile.py`

**Step 1: Update sphinx-apidoc path (line 68)**

```
- session.run("sphinx-apidoc", f"--templatedir={templates}", "-o", modules, "sepal_ui")
+ session.run("sphinx-apidoc", f"--templatedir={templates}", "-o", modules, "pysepal")
```

**Step 2: Update mypy path (line 83)**

```
- test_files = session.posargs or ["sepal_ui"]
+ test_files = session.posargs or ["pysepal"]
```

**Step 3: Commit**

```bash
git add noxfile.py
git commit -m "build: update noxfile.py paths from sepal_ui to pysepal"
```

---

### Task 6: Update .readthedocs.yaml

**Files:**

- Modify: `.readthedocs.yaml`

**Step 1: Update sphinx-apidoc path (line 19)**

```
- - sphinx-apidoc --force --module-first --templatedir=docs/source/_templates/apidoc -o docs/source/modules ./sepal_ui
+ - sphinx-apidoc --force --module-first --templatedir=docs/source/_templates/apidoc -o docs/source/modules ./pysepal
```

**Step 2: Commit**

```bash
git add .readthedocs.yaml
git commit -m "build: update .readthedocs.yaml sphinx-apidoc path to pysepal"
```

---

### Task 7: Update CI workflow paths

**Files:**

- Modify: `.github/workflows/unit.yml`

**Step 1: Update template app test paths (lines 107-109)**

```
-       - name: build the template panel application
-         run: pytest --nbmake sepal_ui/templates/panel_app/ui.ipynb
-       - name: build the template map application
-         run: pytest --nbmake sepal_ui/templates/map_app/ui.ipynb
+       - name: build the template panel application
+         run: pytest --nbmake pysepal/templates/panel_app/ui.ipynb
+       - name: build the template map application
+         run: pytest --nbmake pysepal/templates/map_app/ui.ipynb
```

**Step 2: Commit**

```bash
git add .github/workflows/unit.yml
git commit -m "ci: update template test paths from sepal_ui to pysepal"
```

---

### Task 8: Add dual-read logic to pysepal/conf.py

**Files:**

- Modify: `pysepal/conf.py`

**Step 1: Update the config initialization to use dual-read**

The file path (`~/.sepal-ui-config`) and section name (`sepal-ui`) stay the same for backward compatibility. No changes needed to `conf.py` itself for Phase 2 — the config file path and section name are deliberately kept as-is.

Note: this task requires NO code changes. The design decision is to keep `~/.sepal-ui-config` and `[sepal-ui]` unchanged. Document this explicitly.

**Step 2: Commit** (skip — no changes)

---

### Task 9: Add dual-read for [sepal-ui] in module_deploy

**Files:**

- Modify: `pysepal/bin/module_deploy.py:192`

**Step 1: Update the pyproject.toml section read to accept both names**

Replace the single-key read at line 192:

```python
# Before:
tomli.load("pyproject.toml")["sepal-ui"]["init-notebook"]

# After:
_cfg = tomli.load("pyproject.toml")
try:
    _cfg["pysepal"]["init-notebook"]
except KeyError:
    _cfg["sepal-ui"]["init-notebook"]
```

**Step 2: Also update freeze_sepal_ui to handle both package names (lines 131-151)**

The function searches for `sepal_ui` in requirements.txt lines and writes `sepal_ui==version`. Update to also match `pysepal`:

```python
def freeze_sepal_ui(file: Union[str, Path]) -> None:
    """Set the sepal version to the currently used pysepal version.

    Args:
        file: the requirements file
    """
    file = Path(file)
    text = file.read_text().split("\n")

    # search for the pysepal or sepal_ui line
    idx, _ = next(
        (i, il) for i, il in enumerate(text)
        if "#" not in il and ("pysepal" in il or "sepal_ui" in il)
    )

    text[idx] = f"pysepal=={pysepal.__version__}"

    file.write_text("\n".join(text))

    print(
        f"pysepal version have been freezed to  {Style.BRIGHT}{pysepal.__version__}{Style.NORMAL}"
    )

    return
```

Also update the import at line 24:

```python
- import sepal_ui
+ import pysepal
```

And the welcome message at line 186:

```python
- print(f"{Fore.YELLOW}sepal-ui module deployment tool{Fore.RESET}")
+ print(f"{Fore.YELLOW}pysepal module deployment tool{Fore.RESET}")
```

And the duplicate lib list at line 68:

```python
- libs = ["jupyter", "voila", "tomli", "sepal_ui"]
+ libs = ["jupyter", "voila", "tomli", "pysepal", "sepal_ui"]
```

**Step 3: Commit**

```bash
git add pysepal/bin/module_deploy.py
git commit -m "feat: update module_deploy for pysepal with dual-read [sepal-ui]/[pysepal]"
```

---

### Task 10: Update tests/check_warnings.py

**Files:**

- Modify: `tests/check_warnings.py`

**Step 1: Update the deprecation regex (line 7)**

The shim now emits a slightly different message. Update the filter:

```python
- _SEPAL_DEPRECATION_RE = re.compile(r"The 'sepal_ui' package is deprecated")
+ _SEPAL_DEPRECATION_RE = re.compile(r"The 'sepal_ui' package is deprecated")
```

Actually this regex still matches the shim's message ("The 'sepal_ui' package is deprecated and has been renamed to 'pysepal'"), so no change is needed. Just verify it still matches.

**Step 2: Commit** (skip — no changes needed)

---

### Task 11: Run tests to verify PR B1 state

**Step 1: Run the test suite**

Run: `conda activate sepal_ui && nox -s test -- -x -q 2>&1 | tail -20`

Expected: Many tests will FAIL because internal imports still say `from sepal_ui.X`. This is expected. The shim should redirect them, but some direct relative imports within the package may not go through the shim. PR B2 will fix this.

**Step 2: Verify the shim works for external imports**

Run: `python -c "from sepal_ui.sepalwidgets import AppBar; print('OK')"`
Expected: OK (with deprecation warning)

Run: `python -c "from pysepal.sepalwidgets import AppBar; print('OK')"`
Expected: OK (no warning)

---

## PR B2: Internal Import Rename

### Task 12: Mechanical import rename across all .py files in pysepal/

**Files:**

- Modify: All ~100+ `.py` files in `pysepal/`

**Step 1: Run bulk find-and-replace**

Run the following to replace all `from sepal_ui.` with `from pysepal.` and `import sepal_ui.` with `import pysepal.` across all Python files in the pysepal directory:

```bash
find pysepal -name '*.py' -exec sed -i 's/from sepal_ui\./from pysepal./g' {} +
find pysepal -name '*.py' -exec sed -i 's/import sepal_ui\./import pysepal./g' {} +
find pysepal -name '*.py' -exec sed -i 's/import sepal_ui$/import pysepal/g' {} +
```

**Step 2: Verify no stale imports remain inside pysepal/**

Run: `grep -rn "from sepal_ui\." pysepal/ --include='*.py' | grep -v "__pycache__"`
Expected: no output

Run: `grep -rn "import sepal_ui" pysepal/ --include='*.py' | grep -v "__pycache__"`
Expected: no output

**Step 3: Run ruff to fix import sorting**

Run: `ruff check pysepal/ --fix`

**Step 4: Commit**

```bash
git add pysepal/
git commit -m "refactor: rename all internal imports from sepal_ui to pysepal"
```

---

### Task 13: Rename imports in tests/

**Files:**

- Modify: All test files in `tests/`

**Step 1: Run bulk find-and-replace on test files**

```bash
find tests -name '*.py' -exec sed -i 's/from sepal_ui\./from pysepal./g' {} +
find tests -name '*.py' -exec sed -i 's/import sepal_ui\./import pysepal./g' {} +
find tests -name '*.py' -exec sed -i 's/import sepal_ui$/import pysepal/g' {} +
```

**Step 2: Verify no stale imports remain**

Run: `grep -rn "from sepal_ui\.\|import sepal_ui" tests/ --include='*.py' | grep -v "__pycache__"`
Expected: no output (except possibly in `check_warnings.py` which references the deprecation message string — that's fine)

**Step 3: Run ruff to fix import sorting**

Run: `ruff check tests/ --fix`

**Step 4: Commit**

```bash
git add tests/
git commit -m "refactor: rename all test imports from sepal_ui to pysepal"
```

---

### Task 14: Update docs/source/conf.py

**Files:**

- Modify: `docs/source/conf.py`

**Step 1: Update sys.path insert (line 39)**

```python
- sys.path.insert(0, os.path.abspath("../../sepal_ui/bin"))
+ sys.path.insert(0, os.path.abspath("../../pysepal/bin"))
```

**Step 2: Update import (line 41)**

```python
- from sepal_ui import __author__, __version__  # noqa: E402
+ from pysepal import __author__, __version__  # noqa: E402
```

**Step 3: Update project name (line 52)**

```python
- project = "sepal-ui"
+ project = "pysepal"
```

**Step 4: Update logo text (line 117)**

```python
- "text": "sepal-ui",
+ "text": "pysepal",
```

**Step 5: Update github_repo in html_context (line 143)**

```python
- "github_repo": "sepal_ui",
+ "github_repo": "sepal_ui",
```

Note: keep this as `sepal_ui` for now — the GitHub repo hasn't been renamed yet (Phase 3).

**Step 6: Update deprecation warning filter (lines 21-35)**

The filter should now catch both the old `pysepal/__init__.py` warning (removed) and the shim warning. Update the filter strings to match the shim's new message:

```python
warnings.filterwarnings(
    "ignore",
    message="The 'sepal_ui' package is deprecated and has been renamed to 'pysepal'.*",
    category=DeprecationWarning,
)

doc_warning_filter = (
    "ignore:The 'sepal_ui' package is deprecated and has been renamed to 'pysepal'.*:"
    "DeprecationWarning"
)
```

**Step 7: Commit**

```bash
git add docs/source/conf.py
git commit -m "docs: update docs/source/conf.py imports and project name to pysepal"
```

---

### Task 15: Regenerate docs/source/modules/ RST files

**Files:**

- Delete: all `docs/source/modules/sepal_ui.*.rst` files
- Generate: new `docs/source/modules/pysepal.*.rst` files

**Step 1: Delete old module RST files**

```bash
rm -f docs/source/modules/sepal_ui*.rst
rm -f docs/source/modules/modules.rst
```

**Step 2: Regenerate using sphinx-apidoc**

```bash
sphinx-apidoc --force --module-first --templatedir=docs/source/_templates/apidoc -o docs/source/modules pysepal
```

**Step 3: Verify new files exist**

Run: `ls docs/source/modules/pysepal*.rst`
Expected: `pysepal.rst`, `pysepal.aoi.rst`, `pysepal.mapping.rst`, etc.

**Step 4: Update any docs RST files that reference the old module names**

Search docs for `sepal_ui.` references in toctree directives and cross-references:

```bash
grep -rn "sepal_ui" docs/source/ --include='*.rst'
```

Update any found references.

**Step 5: Commit**

```bash
git add docs/source/modules/
git commit -m "docs: regenerate module RST files for pysepal"
```

---

### Task 16: Run full test suite

**Step 1: Run tests**

Run: `conda activate sepal_ui && nox -s test -- -x -q`
Expected: all tests pass

**Step 2: Run docs build**

Run: `conda activate sepal_ui && nox -s docs`
Expected: builds without unexpected warnings

**Step 3: Run entry point tests**

Run: `conda activate sepal_ui && nox -s bin`
Expected: all entry points respond to --help

---

## PR B3: Notebooks + Templates + Docs Cleanup

### Task 17: Update template requirements.txt files

**Files:**

- Modify: `pysepal/templates/panel_app/requirements.txt:8`
- Modify: `pysepal/templates/map_app/requirements.txt:8`

**Step 1: Update both files**

In both files, change line 8:

```
- sepal_ui
+ pysepal
```

Also update the comment on line 6:

```
- # the base lib to run any sepal_ui based app
+ # the base lib to run any pysepal based app
```

**Step 2: Commit**

```bash
git add pysepal/templates/*/requirements.txt
git commit -m "build: update template requirements.txt from sepal_ui to pysepal"
```

---

### Task 18: Update template pyproject.toml files

**Files:**

- Modify: `pysepal/templates/panel_app/pyproject.toml`
- Modify: `pysepal/templates/map_app/pyproject.toml`

**Step 1: Update section names**

In `panel_app/pyproject.toml` (line 4):

```toml
- [sepal-ui]
+ [pysepal]
```

In `map_app/pyproject.toml` (line 1):

```toml
- [sepal-ui]
+ [pysepal]
```

**Step 2: Commit**

```bash
git add pysepal/templates/*/pyproject.toml
git commit -m "build: update template pyproject.toml section from [sepal-ui] to [pysepal]"
```

---

### Task 19: Update template noxfile.py files

**Files:**

- Modify: `pysepal/templates/panel_app/noxfile.py:20`
- Modify: `pysepal/templates/map_app/noxfile.py:20`

**Step 1: Update the pyproject.toml key read (line 20 in both)**

```python
- init_notebook = tomli.load("pyproject.toml")["sepal-ui"]["init-notebook"]
+ _cfg = tomli.load("pyproject.toml")
+ try:
+     init_notebook = _cfg["pysepal"]["init-notebook"]
+ except KeyError:
+     init_notebook = _cfg["sepal-ui"]["init-notebook"]
```

Note: dual-read so that existing downstream modules with `[sepal-ui]` still work.

**Step 2: Commit**

```bash
git add pysepal/templates/*/noxfile.py
git commit -m "build: update template noxfiles with dual-read [pysepal]/[sepal-ui]"
```

---

### Task 20: Update template Python files

**Files:**

- Modify: All `.py` files in `pysepal/templates/panel_app/component/` and `pysepal/templates/map_app/component/`

**Step 1: Bulk rename imports in template Python files**

```bash
find pysepal/templates -name '*.py' -exec sed -i 's/from sepal_ui\./from pysepal./g' {} +
find pysepal/templates -name '*.py' -exec sed -i 's/import sepal_ui\./import pysepal./g' {} +
find pysepal/templates -name '*.py' -exec sed -i 's/import sepal_ui$/import pysepal/g' {} +
```

**Step 2: Verify**

Run: `grep -rn "from sepal_ui\.\|import sepal_ui" pysepal/templates/ --include='*.py'`
Expected: no output

**Step 3: Commit**

```bash
git add pysepal/templates/
git commit -m "refactor: update template Python imports from sepal_ui to pysepal"
```

---

### Task 21: Update Jupyter notebooks

**Files:**

- Modify: All 11 tracked `.ipynb` files

**Step 1: Bulk replace in notebooks**

Notebooks are JSON. Use sed carefully (notebooks store code in `"source"` arrays):

```bash
# Update imports in all tracked notebooks
git ls-files '*.ipynb' | xargs sed -i 's/from sepal_ui/from pysepal/g'
git ls-files '*.ipynb' | xargs sed -i 's/import sepal_ui/import pysepal/g'
```

**Step 2: Verify**

Run: `git ls-files '*.ipynb' | xargs grep -l "sepal_ui" | head`
Expected: possibly some notebooks with `sepal_ui` in markdown text (explanations), but no import statements

**Step 3: Strip notebook output**

Run: `pre-commit run nbstripout --all-files`

**Step 4: Commit**

```bash
git add '*.ipynb'
git commit -m "refactor: update notebook imports from sepal_ui to pysepal"
```

---

### Task 22: Update module_factory.py template references

**Files:**

- Modify: `pysepal/bin/module_factory.py:152,176`

**Step 1: The GitHub URL placeholder stays as-is**

Lines 152 and 176 replace `https://github.com/12rambau/sepal_ui` with the user's URL. This is Phase 3 (repo rename) so leave these unchanged for now.

**Step 2: Update the welcome message (line 191)**

```python
- print(f"{Fore.YELLOW}sepal-ui module factory{Fore.RESET}")
+ print(f"{Fore.YELLOW}pysepal module factory{Fore.RESET}")
```

**Step 3: Commit**

```bash
git add pysepal/bin/module_factory.py
git commit -m "refactor: update module_factory welcome message to pysepal"
```

---

### Task 23: Update remaining docs RST files

**Files:**

- Modify: `docs/source/index.rst`
- Modify: `docs/source/start/index.rst`
- Modify: `docs/source/start/installation.rst`
- Modify: `README.rst`

**Step 1: Search for all remaining sepal_ui / sepal-ui references in docs**

```bash
grep -rn "sepal.ui\|sepal_ui" docs/source/ --include='*.rst' | grep -v modules/
grep -rn "sepal.ui\|sepal_ui" README.rst
```

**Step 2: Update import examples and package references**

In each file, update:

- `pip install sepal-ui` -> `pip install pysepal`
- `import sepal_ui` -> `import pysepal`
- `from sepal_ui` -> `from pysepal`
- Keep deprecation banner text that references the old name (it's intentional)
- Keep GitHub URLs unchanged (Phase 3)

**Step 3: Commit**

```bash
git add docs/ README.rst
git commit -m "docs: update documentation references from sepal_ui to pysepal"
```

---

### Task 24: Clean up stale build artifacts

**Step 1: Check for stale build/ directory**

```bash
ls build/ 2>/dev/null && echo "stale build dir exists"
```

**Step 2: Remove and gitignore if needed**

```bash
rm -rf build/ dist/ *.egg-info
# Verify build/ is in .gitignore
grep "build/" .gitignore || echo "build/" >> .gitignore
```

**Step 3: Commit if changes were made**

```bash
git add .gitignore
git commit -m "chore: clean up stale build artifacts"
```

---

### Task 25: Final validation

**Step 1: Verify no stale sepal_ui references (except shim and intentional mentions)**

```bash
rg -n "\bsepal_ui\b" --glob '!*.ipynb' --glob '!sepal_ui/' --glob '!.nox/' --glob '!build/' --glob '!*.egg-info/' --glob '!CHANGELOG.md' --glob '!.plans/'
```

Expected: only matches in:

- `sepal_ui/__init__.py` (the shim)
- `pysepal/conf.py` (config file path `~/.sepal-ui-config` and section name)
- `pysepal/scripts/utils.py` (set_config with `sepal-ui` section)
- `pysepal/bin/module_deploy.py` (dual-read logic, duplicate lib list)
- `pysepal/bin/module_factory.py` (GitHub URL placeholder — Phase 3)
- `tests/check_warnings.py` (deprecation filter regex)
- `docs/` (deprecation banners, migration notices)
- `README.rst` (deprecation banner)
- `docs/plans/` (design/plan documents)
- `pysepal/frontend/resize_trigger.py` (CSS class `sepal-ui-script`)
- `pysepal/frontend/styles.py` (internal variable `sepal_ui_css`)
- Logger namespace `sepalui` (deliberately unchanged)

**Step 2: Run full test suite**

Run: `conda activate sepal_ui && nox -s test -- -x -q`
Expected: all tests pass

**Step 3: Run docs build**

Run: `conda activate sepal_ui && nox -s docs`
Expected: builds successfully

**Step 4: Run entry point tests**

Run: `conda activate sepal_ui && nox -s bin`
Expected: all entry points work

**Step 5: Verify shim still works**

```bash
python -c "
import warnings
warnings.simplefilter('always')
from sepal_ui.sepalwidgets import AppBar
from sepal_ui.mapping import SepalMap
from sepal_ui.aoi import AoiModel
print('Shim OK: all imports redirected')
"
```

Expected: prints "Shim OK" with DeprecationWarning

**Step 6: Verify pysepal imports work**

```bash
python -c "
from pysepal.sepalwidgets import AppBar
from pysepal.mapping import SepalMap
from pysepal.aoi import AoiModel
print('Direct OK: all imports work')
"
```

Expected: prints "Direct OK" with no warnings

---

## Summary: What is deliberately NOT renamed

| Item                | Location                     | Reason                         |
| ------------------- | ---------------------------- | ------------------------------ |
| Config file path    | `~/.sepal-ui-config`         | Would break user settings      |
| Config section      | `[sepal-ui]` in ConfigParser | Would break user settings      |
| Logger namespace    | `sepalui.*`                  | Would break downstream logging |
| CSS class           | `.sepal-ui-script`           | DOM-level, no benefit          |
| GitHub URLs         | `12rambau/sepal_ui`          | Phase 3                        |
| PyPI/RTD/conda URLs | `sepal-ui`                   | Phase 3                        |
