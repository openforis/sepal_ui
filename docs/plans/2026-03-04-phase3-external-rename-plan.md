# Phase 3: External Infrastructure Rename Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Update all external URLs (GitHub, PyPI, conda-forge), docstrings, and comments from `sepal_ui`/`sepal-ui`/`12rambau` to `pysepal`/`openforis/pysepal`, and provide guidance for external platform actions.

**Architecture:** Single PR with all code changes. After merge, the GitHub repo is renamed and external platforms updated. ReadTheDocs URLs are deliberately left unchanged (deferred to separate issue).

**Tech Stack:** RST documentation, Python docstrings, `pyproject.toml`, Sphinx config, Jupyter notebooks, CSS comments.

---

## Task 1: Update pyproject.toml URLs

**Files:**

- Modify: `pyproject.toml:68-69`

**Step 1: Update Homepage and Download URLs**

```
- Homepage = "https://github.com/12rambau/sepal_ui"
- Download = "https://github.com/12rambau/sepal_ui/archive/v_${metadata:version}.tar.gz"
+ Homepage = "https://github.com/openforis/pysepal"
+ Download = "https://github.com/openforis/pysepal/archive/v_${metadata:version}.tar.gz"
```

**Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "build: update pyproject.toml URLs to openforis/pysepal"
```

---

## Task 2: Update docs/source/conf.py external references

**Files:**

- Modify: `docs/source/conf.py:128,133,142-143`

**Step 1: Update GitHub icon link (line 128)**

```python
# Before:
            "url": "https://github.com/12rambau/sepal_ui",
# After:
            "url": "https://github.com/openforis/pysepal",
```

**Step 2: Update PyPI icon link (line 133)**

```python
# Before:
            "url": "https://pypi.org/project/sepal-ui/",
# After:
            "url": "https://pypi.org/project/pysepal/",
```

**Step 3: Update html_context (lines 142-143)**

```python
# Before:
    "github_user": "12rambau",
    "github_repo": "sepal_ui",
# After:
    "github_user": "openforis",
    "github_repo": "pysepal",
```

**Step 4: Commit**

```bash
git add docs/source/conf.py
git commit -m "docs: update conf.py GitHub and PyPI URLs to openforis/pysepal"
```

---

## Task 3: Update README.rst badges and URLs

**Files:**

- Modify: `README.rst`

**Step 1: Update title (line 3)**

```rst
- Sepal_ui
+ pysepal
```

And underline (line 4):

```rst
- --------
+ --------
```

Note: underline must be >= length of title. "pysepal" is 7 chars, "--------" is 8, that's fine.

**Step 2: Update deprecation warning (lines 6-9)**

```rst
- .. warning::
-
-     `sepal-ui` is in deprecation transition and will be renamed to `pysepal`.
-     This release is maintained for compatibility while migration work is completed.
+ .. note::
+
+     `sepal-ui` has been renamed to `pysepal`. The old import path ``import sepal_ui`` still
+     works via a compatibility shim but will be removed in a future release.
```

**Step 3: Update PyPI badges (lines 35-44)**

```rst
- .. image:: https://img.shields.io/pypi/v/sepal-ui?color=orange&logo=pypi&logoColor=white
-     :target: https://pypi.org/project/sepal-ui/
+ .. image:: https://img.shields.io/pypi/v/pysepal?color=orange&logo=pypi&logoColor=white
+     :target: https://pypi.org/project/pysepal/

- .. image:: https://img.shields.io/conda/vn/conda-forge/sepal-ui?color=orange&logo=anaconda&logoColor=white
-     :target: https://anaconda.org/conda-forge/sepal-ui
+ .. image:: https://img.shields.io/conda/vn/conda-forge/pysepal?color=orange&logo=anaconda&logoColor=white
+     :target: https://anaconda.org/conda-forge/pysepal

- .. image:: https://img.shields.io/pypi/pyversions/sepal-ui?color=orange&logo=python&logoColor=white
-    :target: https://pypi.org/project/sepal-ui/
+ .. image:: https://img.shields.io/pypi/pyversions/pysepal?color=orange&logo=python&logoColor=white
+    :target: https://pypi.org/project/pysepal/
```

**Step 4: Update GitHub Actions badge (lines 47-49)**

```rst
- .. image:: https://img.shields.io/github/actions/workflow/status/12rambau/sepal_ui/unit.yml?logo=github&logoColor=white
-     :target: https://github.com/12rambau/sepal_ui/actions/workflows/unit.yml
+ .. image:: https://img.shields.io/github/actions/workflow/status/openforis/pysepal/unit.yml?logo=github&logoColor=white
+     :target: https://github.com/openforis/pysepal/actions/workflows/unit.yml
```

**Step 5: Update CodeClimate badge (lines 51-53)**

```rst
- .. image:: https://img.shields.io/codeclimate/maintainability/12rambau/sepal_ui?logo=codeclimate&logoColor=white
-     :target: https://codeclimate.com/github/12rambau/sepal_ui/maintainability
+ .. image:: https://img.shields.io/codeclimate/maintainability/openforis/pysepal?logo=codeclimate&logoColor=white
+     :target: https://codeclimate.com/github/openforis/pysepal/maintainability
```

**Step 6: Update Codecov badge (lines 55-57)**

```rst
- .. image:: https://img.shields.io/codecov/c/github/12rambau/sepal_ui?logo=codecov&logoColor=white
-     :target: https://codecov.io/gh/12rambau/sepal_ui
+ .. image:: https://img.shields.io/codecov/c/github/openforis/pysepal?logo=codecov&logoColor=white
+     :target: https://codecov.io/gh/openforis/pysepal
```

**Step 7: Update body text (line 78)**

```rst
- :code:`sepal_ui` is a lib designed to create elegant python based dashboard in the `SEPAL environment <https://sepal.io/>`__.
+ :code:`pysepal` is a lib designed to create elegant python based dashboard in the `SEPAL environment <https://sepal.io/>`__.
```

**Step 8: Update image URLs (lines 92-96)**

```rst
- .. |map-app| image:: https://raw.githubusercontent.com/12rambau/sepal_ui/main/docs/source/_image/demo-map-app.png
+ .. |map-app| image:: https://raw.githubusercontent.com/openforis/pysepal/main/docs/source/_image/demo-map-app.png

- .. |panel-app| image:: https://raw.githubusercontent.com/12rambau/sepal_ui/main/docs/source/_image/demo-panel-app.png
+ .. |panel-app| image:: https://raw.githubusercontent.com/openforis/pysepal/main/docs/source/_image/demo-panel-app.png
```

**Step 9: Commit**

```bash
git add README.rst
git commit -m "docs: update README.rst badges and URLs to openforis/pysepal"
```

---

## Task 4: Update CONTRIBUTING.rst

**Files:**

- Modify: `CONTRIBUTING.rst`

**Step 1: Update clone URL (line 12-13)**

```rst
- $ git clone https://github.com/<github id>/sepal_ui.git
- $ cd sepal_ui
+ $ git clone https://github.com/<github id>/pysepal.git
+ $ cd pysepal
```

**Step 2: Update branching image URL (line 46)**

```rst
- .. figure:: https://raw.githubusercontent.com/12rambau/sepal_ui/main/docs/source/_image/branching_system.png
+ .. figure:: https://raw.githubusercontent.com/openforis/pysepal/main/docs/source/_image/branching_system.png
```

**Step 3: Update commitizen reference (line 148)**

```rst
- It should modify for you the version number in :code:`sepal_ui/__init__.py`, :code:`setup.py`, and :code:`.cz.yaml` according to semantic versioning thanks to the conventional commit that we use in the lib.
+ It should modify for you the version number in :code:`pysepal/__init__.py`, :code:`setup.py`, and :code:`.cz.yaml` according to semantic versioning thanks to the conventional commit that we use in the lib.
```

**Step 4: Update PyPI link (line 162)**

```rst
- The CI should take everything in control from here and execute the :code:`Upload Python Package` GitHub Action that is publishing the new version on `PyPi <https://pypi.org/project/sepal-ui/>`_.
+ The CI should take everything in control from here and execute the :code:`Upload Python Package` GitHub Action that is publishing the new version on `PyPi <https://pypi.org/project/pysepal/>`_.
```

**Step 5: Update SEPAL init script URL (line 164)**

```rst
- Once it's done you need to trigger the rebuild of SEPAL. modify the following `file <https://github.com/openforis/sepal/blob/master/modules/sandbox/docker/script/init_sepal_ui.sh>`_ with the latest version number and the rebuild will start automatically.
+ Once it's done you need to trigger the rebuild of SEPAL. modify the following `file <https://github.com/openforis/sepal/blob/master/modules/sandbox/docker/script/init_pysepal.sh>`_ with the latest version number and the rebuild will start automatically.
```

**Step 6: Update api-doc section (line 214)**

```rst
- We are using :code:`api-doc` to build the documentation of the lib so if you want to see the API related documentation in your local build you need to run the following lines from the :code:`sepal_ui` folder:
+ We are using :code:`api-doc` to build the documentation of the lib so if you want to see the API related documentation in your local build you need to run the following lines from the :code:`pysepal` folder:
```

**Step 7: Commit**

```bash
git add CONTRIBUTING.rst
git commit -m "docs: update CONTRIBUTING.rst URLs to openforis/pysepal"
```

---

## Task 5: Update docs/source/index.rst

**Files:**

- Modify: `docs/source/index.rst`

**Step 1: Update title (line 3)**

```rst
- Sepal_ui
+ pysepal
```

**Step 2: Update deprecation warning (lines 6-9)**

```rst
- .. warning::
-
-     `sepal-ui` is in deprecation transition and will be renamed to `pysepal`.
-     Keep using `sepal-ui` for now, and plan migration to `pysepal` as the new canonical package name.
+ .. note::
+
+     `sepal-ui` has been renamed to `pysepal`. The old import path ``import sepal_ui`` still
+     works via a compatibility shim but will be removed in a future release.
```

**Step 3: Update demo GIF URL (line 33)**

```rst
- .. image:: https://raw.githubusercontent.com/12rambau/sepal_ui/main/docs/source/_image/sepal_ui_demo.gif
+ .. image:: https://raw.githubusercontent.com/openforis/pysepal/main/docs/source/_image/sepal_ui_demo.gif
```

**Step 4: Commit**

```bash
git add docs/source/index.rst
git commit -m "docs: update index.rst URLs and deprecation notice"
```

---

## Task 6: Update docs/source/start/index.rst

**Files:**

- Modify: `docs/source/start/index.rst`

**Step 1: Update deprecation warning (lines 4-7)**

```rst
- .. warning::
-
-     `sepal-ui` is in deprecation transition and will be renamed to `pysepal`.
-     New projects should track migration updates and adopt `pysepal` when available.
+ .. note::
+
+     `sepal-ui` has been renamed to `pysepal`. The old import path ``import sepal_ui`` still
+     works via a compatibility shim but will be removed in a future release.
```

**Step 2: Update demo GIF URL (line 19)**

```rst
- .. image:: https://raw.githubusercontent.com/12rambau/sepal_ui/main/docs/source/_image/sepal_ui_demo.gif
+ .. image:: https://raw.githubusercontent.com/openforis/pysepal/main/docs/source/_image/sepal_ui_demo.gif
```

**Step 3: Commit**

```bash
git add docs/source/start/index.rst
git commit -m "docs: update start/index.rst URLs and deprecation notice"
```

---

## Task 7: Update docs/source/start/installation.rst

**Files:**

- Modify: `docs/source/start/installation.rst`

**Step 1: Update deprecation warning (lines 4-7)**

```rst
- .. warning::
-
-    `sepal-ui` is in deprecation transition and will be renamed to `pysepal`.
-    This page documents the current package while migration is in progress.
+ .. note::
+
+    `sepal-ui` has been renamed to `pysepal`. The old import path ``import sepal_ui`` still
+    works via a compatibility shim but will be removed in a future release.
```

**Step 2: Update GitHub repo link (line 26)**

```rst
- The source of pysepal can be installed from the `GitHub repo <https://github.com/12rambau/sepal_ui>`_:
+ The source of pysepal can be installed from the `GitHub repo <https://github.com/openforis/pysepal>`_:
```

**Step 3: Update pip install from git (line 30)**

```rst
-    python -m pip install git+git://github.com/12rambau/sepal_ui.git#egg=pysepal
+    python -m pip install git+git://github.com/openforis/pysepal.git#egg=pysepal
```

**Step 4: Update git clone (lines 37-38)**

```rst
-    git clone https://github.com/12rambau/sepal_ui.git
-    cd sepal_ui/
+    git clone https://github.com/openforis/pysepal.git
+    cd pysepal/
```

**Step 5: Commit**

```bash
git add docs/source/start/installation.rst
git commit -m "docs: update installation.rst URLs to openforis/pysepal"
```

---

## Task 8: Update tutorial docs

**Files:**

- Modify: `docs/source/tutorials/solara.rst`
- Modify: `docs/source/tutorials/send-to-sepal.rst`
- Modify: `docs/source/tutorials/send-to-heroku.rst`
- Modify: `docs/source/tutorials/create-module.rst`

**Step 1: Update solara.rst clone URL (lines 51-53)**

```rst
-     git clone -b solara3 https://github.com/openforis/sepal_ui.git
-     cd sepal_ui
+     git clone -b solara3 https://github.com/openforis/pysepal.git
+     cd pysepal
```

**Step 2: Update solara.rst notebook path references (line 152)**

```rst
- Start Jupyter Lab and run these notebooks from ``sepal_ui/notebooks``:
+ Start Jupyter Lab and run these notebooks from ``pysepal/notebooks``:
```

**Step 3: Update solara.rst cd command (line 156)**

```rst
-     cd sepal_ui/notebooks
+     cd pysepal/notebooks
```

**Step 4: Update solara.rst .env reference (line 188)**

```rst
- Create a ``.env`` file in the ``sepal_ui`` root directory:
+ Create a ``.env`` file in the ``pysepal`` root directory:
```

**Step 5: Update solara.rst cd path (line 205-206)**

```rst
-     # Navigate back to the main sepal_ui directory
-     cd /path/to/sepal_ui
+     # Navigate back to the main pysepal directory
+     cd /path/to/pysepal
```

**Step 6: Update send-to-sepal.rst git URL (line 72)**

```rst
-         git+https://github.com/12rambau/sepal_ui.git#egg=pysepal
+         git+https://github.com/openforis/pysepal.git#egg=pysepal
```

**Step 7: Update send-to-heroku.rst URLs (lines 15, 19, 24)**

```rst
- This methodology has been used to deploy the `demo app <https://sepal-ui.herokuapp.com>`__ of the framework. the source code can be found `here <https://github.com/12rambau/sepal_ui_template/tree/heroku>`__.
+ This methodology has been used to deploy the `demo app <https://sepal-ui.herokuapp.com>`__ of the framework. the source code can be found `here <https://github.com/openforis/sepal_ui_template/tree/heroku>`__.

- You can still reach the development team in the `issue tracker <https://github.com/12rambau/sepal_ui/issues>`__
+ You can still reach the development team in the `issue tracker <https://github.com/openforis/pysepal/issues>`__

- An `issue <https://github.com/12rambau/sepal_ui/issues/336>`__
+ An `issue <https://github.com/openforis/pysepal/issues/336>`__
```

**Step 8: Update create-module.rst template references (lines 162, 224)**

```rst
- This script cloned the `template repository <https://github.com/12rambau/sepal_ui_template>`_
+ This script cloned the `template repository <https://github.com/openforis/sepal_ui_template>`_

- The `sepal_ui_template <https://github.com/12rambau/sepal_ui_template>`__
+ The `sepal_ui_template <https://github.com/openforis/sepal_ui_template>`__
```

**Step 9: Commit**

```bash
git add docs/source/tutorials/
git commit -m "docs: update tutorial URLs to openforis/pysepal"
```

---

## Task 9: Update template doc files and notebooks

**Files:**

- Modify: `pysepal/templates/map_app/doc/en.rst`
- Modify: `pysepal/templates/panel_app/doc/en.rst`
- Modify: `pysepal/templates/map_app/ui.ipynb`
- Modify: `pysepal/templates/panel_app/ui.ipynb`

**Step 1: Update template doc en.rst files (line 10 in both)**

In both `pysepal/templates/map_app/doc/en.rst` and `pysepal/templates/panel_app/doc/en.rst`:

```rst
-     Please open an issue on their repository : https://github.com/12rambau/sepal_ui/issues/new
+     Please open an issue on their repository : https://github.com/openforis/pysepal/issues/new
```

**Step 2: Update map_app/ui.ipynb links**

In the cell containing the drawer links:

```python
# Before:
code_link = "https://github.com/12rambau/sepal_ui"
wiki_link = "https://github.com/12rambau/sepal_ui/blob/main/doc/en.rst"
issue_link = "https://github.com/12rambau/sepal_ui/issues/new"

# After:
code_link = "https://github.com/openforis/pysepal"
wiki_link = "https://github.com/openforis/pysepal/blob/main/doc/en.rst"
issue_link = "https://github.com/openforis/pysepal/issues/new"
```

**Step 3: Update panel_app/ui.ipynb links**

In the cell containing the drawer links:

```python
# Before:
code_link = "https://github.com/12rambau/sepal_ui/"
wiki_link = "https://github.com/12rambau/sepal_ui/blob/master/doc/en.rst"
issue_link = "https://github.com/12rambau/sepal_ui/issues/new"

# After:
code_link = "https://github.com/openforis/pysepal/"
wiki_link = "https://github.com/openforis/pysepal/blob/main/doc/en.rst"
issue_link = "https://github.com/openforis/pysepal/issues/new"
```

**Step 4: Commit**

```bash
git add pysepal/templates/
git commit -m "docs: update template doc and notebook URLs to openforis/pysepal"
```

---

## Task 10: Update module_factory.py placeholder URLs

**Files:**

- Modify: `pysepal/bin/module_factory.py:152,176`

**Step 1: Update the doc replacement URL (line 152)**

```python
# Before:
        text = text.replace("https://github.com/12rambau/sepal_ui", url)
# After:
        text = text.replace("https://github.com/openforis/pysepal", url)
```

**Step 2: Update the drawer link replacement URL (line 176)**

```python
# Before:
    ui_content = ui_content.replace("https://github.com/12rambau/sepal_ui", url)
# After:
    ui_content = ui_content.replace("https://github.com/openforis/pysepal", url)
```

**Step 3: Commit**

```bash
git add pysepal/bin/module_factory.py
git commit -m "refactor: update module_factory placeholder URLs to openforis/pysepal"
```

---

## Task 11: Update module_deploy.py references

**Files:**

- Modify: `pysepal/bin/module_deploy.py:11,112,119`

**Step 1: Update docstring (line 11)**

```python
# Before:
-  sepal-ui version will be bound to the one available when calling the script
# After:
-  pysepal version will be bound to the one available when calling the script
```

**Step 2: Update troubleshooting messages (lines 112, 119)**

```python
# Before:
            print(f"Removing {Style.BRIGHT}ee{Style.NORMAL} from reqs, included in sepal_ui.")
# After:
            print(f"Removing {Style.BRIGHT}ee{Style.NORMAL} from reqs, included in pysepal.")

# Before:
                f"Removing {Style.BRIGHT}earthengine_api{Style.NORMAL} from reqs, included in sepal_ui."
# After:
                f"Removing {Style.BRIGHT}earthengine_api{Style.NORMAL} from reqs, included in pysepal."
```

**Step 3: Commit**

```bash
git add pysepal/bin/module_deploy.py
git commit -m "refactor: update module_deploy references from sepal_ui to pysepal"
```

---

## Task 12: Update module_l10n.py and module_theme.py

**Files:**

- Modify: `pysepal/bin/module_l10n.py:5,45`
- Modify: `pysepal/bin/module_theme.py:5,29,42`

**Step 1: Update module_l10n.py docstring (line 5)**

```python
# Before:
This script will update the parameters shared between all sepal-ui based modules.
# After:
This script will update the parameters shared between all pysepal based modules.
```

**Step 2: Update module_l10n.py welcome message (line 45)**

```python
# Before:
    print(f"{Fore.YELLOW}sepal-ui localisation script{Fore.RESET}")
# After:
    print(f"{Fore.YELLOW}pysepal localisation script{Fore.RESET}")
```

**Step 3: Update module_theme.py docstring (line 5)**

```python
# Before:
This script will update the parameters shared between all sepal-ui based modules.
# After:
This script will update the parameters shared between all pysepal based modules.
```

**Step 4: Update module_theme.py docstring return (line 29)**

```python
# Before:
        True if the theme is covered by sepal-ui
# After:
        True if the theme is covered by pysepal
```

**Step 5: Update module_theme.py welcome message (line 42)**

```python
# Before:
    print(f"{Fore.YELLOW}sepal-ui module theme selection{Fore.RESET}")
# After:
    print(f"{Fore.YELLOW}pysepal module theme selection{Fore.RESET}")
```

**Step 6: Commit**

```bash
git add pysepal/bin/module_l10n.py pysepal/bin/module_theme.py
git commit -m "refactor: update module_l10n and module_theme references to pysepal"
```

---

## Task 13: Update Python package docstrings

**Files:**

- Modify: `pysepal/planetapi/__init__.py:3`
- Modify: `pysepal/mapping/__init__.py:3,5`
- Modify: `pysepal/aoi/__init__.py:3`
- Modify: `pysepal/sepalwidgets/__init__.py:1,3`
- Modify: `pysepal/scripts/__init__.py:1`
- Modify: `pysepal/message/__init__.py:1`
- Modify: `pysepal/frontend/styles.py:151,192`

**Step 1: Update planetapi/**init**.py (line 3)**

```python
# Before:
Package to access all the widget, model and tiles to create an Planet interface in sepal-ui.
# After:
Package to access all the widget, model and tiles to create an Planet interface in pysepal.
```

**Step 2: Update mapping/**init**.py (lines 3, 5)**

```python
# Before:
It is also fully compatible with the **sepal-ui** framework thanks to frontend modifications.
# After:
It is also fully compatible with the **pysepal** framework thanks to frontend modifications.

# Before:
The main object is the ``SepalMap``that should be used in favor of ``Map`` in **sepal-ui** framework.
# After:
The main object is the ``SepalMap``that should be used in favor of ``Map`` in **pysepal** framework.
```

**Step 3: Update aoi/**init**.py (line 3)**

```python
# Before:
Package to access all the widget, model and tiles to create an AOI selection interface available in sepal-ui.
# After:
Package to access all the widget, model and tiles to create an AOI selection interface available in pysepal.
```

**Step 4: Update sepalwidgets/**init**.py (lines 1, 3)**

```python
# Before:
"""All the widgets available in sepal-ui.

Package to access all the widget available in sepal-ui. The widgets are all derived from ``IpyvuetifyWidget`` and ``SepalWidget``. They can be used to build interfaces in applications. ``sepal_ui.sepalwidgets`` include all the widgets from `ìpyvuetify`` and some extra one that are useful to build GIS related applications.
# After:
"""All the widgets available in pysepal.

Package to access all the widget available in pysepal. The widgets are all derived from ``IpyvuetifyWidget`` and ``SepalWidget``. They can be used to build interfaces in applications. ``pysepal.sepalwidgets`` include all the widgets from `ìpyvuetify`` and some extra one that are useful to build GIS related applications.
```

**Step 5: Update scripts/**init**.py (line 1)**

```python
# Before:
"""Gather all the scripts used to support the sepal-ui interface (widgets and map).
# After:
"""Gather all the scripts used to support the pysepal interface (widgets and map).
```

**Step 6: Update message/**init**.py (line 1)**

```python
# Before:
"""Initialization of the ``Translator`` used in the sepal-ui.
# After:
"""Initialization of the ``Translator`` used in pysepal.
```

**Step 7: Update frontend/styles.py (line 151)**

```python
# Before:
        """Custom simple name space to store and access to the sepal_ui colors and with a magic method to display theme."""
# After:
        """Custom simple name space to store and access to the pysepal colors and with a magic method to display theme."""
```

**Step 8: Update frontend/styles.py comment (line 192)**

```python
# Before:
# load custom styling of sepal_ui
# After:
# load custom styling of pysepal
```

**Step 9: Commit**

```bash
git add pysepal/planetapi/__init__.py pysepal/mapping/__init__.py pysepal/aoi/__init__.py pysepal/sepalwidgets/__init__.py pysepal/scripts/__init__.py pysepal/message/__init__.py pysepal/frontend/styles.py
git commit -m "refactor: update package docstrings from sepal-ui to pysepal"
```

---

## Task 14: Update CSS comment URLs

**Files:**

- Modify: `pysepal/frontend/css/custom.css:2,106`
- Modify: `pysepal/solara/common/assets/custom.css:2,101`

**Step 1: Update custom.css header comment (line 2 in both files)**

```css
/* Before: */
 * Customization of the provided css from the different libs used by sepal_ui
/* After: */
 * Customization of the provided css from the different libs used by pysepal
```

**Step 2: Update custom.css issue URL (line 106 in frontend, line 101 in solara)**

```css
/* Before: */
/* Related with https://github.com/12rambau/sepal_ui/issues/893 */
/* After: */
/* Related with https://github.com/openforis/pysepal/issues/893 */
```

**Step 3: Commit**

```bash
git add pysepal/frontend/css/custom.css pysepal/solara/common/assets/custom.css
git commit -m "refactor: update CSS comment URLs to openforis/pysepal"
```

---

## Task 15: Final validation

**Step 1: Check for remaining 12rambau references**

Run: `rg "12rambau" --glob '!CHANGELOG.md' --glob '!docs/plans/' --glob '!.nox/' --glob '!build/'`

Expected: No matches (or only in CHANGELOG.md and docs/plans/).

**Step 2: Check for remaining sepal_ui GitHub URLs**

Run: `rg "github.com.*sepal_ui" --glob '!CHANGELOG.md' --glob '!docs/plans/' --glob '!.nox/' --glob '!sepal_ui/'`

Expected: No matches outside shim directory.

**Step 3: Check for remaining PyPI sepal-ui URLs**

Run: `rg "pypi.org/project/sepal-ui" --glob '!CHANGELOG.md' --glob '!docs/plans/'`

Expected: No matches.

**Step 4: Check for remaining conda-forge sepal-ui URLs**

Run: `rg "conda-forge/sepal-ui" --glob '!CHANGELOG.md' --glob '!docs/plans/'`

Expected: No matches.

**Step 5: Run test suite**

Run: `conda activate pysepal && nox -s test -- -x -q`

Expected: All tests pass.

**Step 6: Verify docs build**

Run: `conda activate pysepal && nox -s docs`

Expected: Builds successfully.

---

## Task 16: Create deferred issues

After the PR is merged, create two GitHub issues:

**Issue 1: Migrate ReadTheDocs project**

Title: `chore: migrate ReadTheDocs from sepal-ui to pysepal`

Body: Update the ReadTheDocs project slug from `sepal-ui` to `pysepal`. This includes:

- Updating the RTD project name/slug in admin settings
- Updating all `sepal-ui.readthedocs.io` URLs in the codebase
- Updating the version switcher JSON URL in `docs/source/conf.py`

**Issue 2: Deprecate ~/.sepal-ui-config**

Title: `chore: deprecate ~/.sepal-ui-config file`

Body: The config file at `~/.sepal-ui-config` stores theme and internationalization preferences. With the move to Solara applications, this data is stored in the browser. Deprecate this config file:

- Add deprecation warning when reading from `~/.sepal-ui-config`
- Eventually remove config file support in a future major release

---

## External Platform Actions (Post-Merge)

### GitHub Repo Rename

1. Go to `github.com/openforis/sepal_ui` → Settings → General
2. Change repository name to `pysepal`
3. GitHub automatically creates a redirect from `openforis/sepal_ui` → `openforis/pysepal`
4. All contributors update their local remotes:
   ```bash
   git remote set-url origin git@github.com:openforis/pysepal.git
   ```

### PyPI

The distribution name is already `pysepal` in `pyproject.toml` (changed in Phase 2). On next release, the package will be published as `pysepal` on PyPI.

Options for the old `sepal-ui` PyPI package:

- Publish a final `sepal-ui` release that depends on `pysepal` (redirect package)
- Or let users follow the deprecation warning naturally

### Conda-Forge

1. Open an issue on `conda-forge/sepal-ui-feedstock` to request package rename
2. Or create a new `pysepal-feedstock` via conda-forge staged-recipes
3. Archive the old `sepal-ui-feedstock` once migration is confirmed
