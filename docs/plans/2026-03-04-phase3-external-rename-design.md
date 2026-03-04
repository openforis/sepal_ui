# Phase 3 Design: External Infrastructure Rename

## Context

Phase 2 (v3.3.0) completed the internal rename: source directory, Python imports, distribution name, and packaging all use `pysepal`. Phase 3 updates the remaining external references: GitHub URLs, PyPI badges, conda-forge badges, and docstrings/comments that still say "sepal-ui" or "sepal_ui".

## Scope

### Changed in Phase 3

| Category                                      | Before                                                             | After                              |
| --------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------- |
| GitHub repo                                   | `openforis/sepal_ui`                                               | `openforis/pysepal`                |
| GitHub URLs in code/docs                      | `github.com/12rambau/sepal_ui` and `github.com/openforis/sepal_ui` | `github.com/openforis/pysepal`     |
| PyPI URLs/badges                              | `pypi.org/project/sepal-ui`                                        | `pypi.org/project/pysepal`         |
| Conda-forge badges                            | `conda-forge/sepal-ui`                                             | `conda-forge/pysepal`              |
| `pyproject.toml` Homepage/Download            | `github.com/12rambau/sepal_ui`                                     | `github.com/openforis/pysepal`     |
| `docs/source/conf.py` github_repo, icon_links | `sepal_ui`, `12rambau/sepal_ui`                                    | `pysepal`, `openforis/pysepal`     |
| Docstrings and comments                       | "sepal-ui" references                                              | "pysepal"                          |
| User-facing print statements                  | "sepal-ui localisation script" etc.                                | "pysepal localisation script" etc. |

### NOT Changed in Phase 3 (deferred — new issues)

| Item                                         | Reason                                 |
| -------------------------------------------- | -------------------------------------- |
| ReadTheDocs URLs (`sepal-ui.readthedocs.io`) | Deferred to separate issue             |
| `~/.sepal-ui-config` file path               | Deferred to separate deprecation issue |
| `[sepal-ui]` ConfigParser section            | Deferred with config file deprecation  |

### NOT Changed (permanent)

| Item                                                 | Reason                                |
| ---------------------------------------------------- | ------------------------------------- |
| `sepalui` logger namespace                           | Would break downstream logging config |
| `.sepal-ui-script` CSS class                         | DOM-level, no user benefit            |
| Crowdin project URL (`crowdin.com/project/sepal-ui`) | Stays as-is                           |
| `sepal_ui/` shim directory                           | Backward compatibility — stays        |

## Approach

**Code-first, platform-after (Approach A):**

1. All code changes in a single PR against the current repo
2. Merge the PR before renaming the GitHub repo
3. After merge, perform external platform actions in order

GitHub auto-redirects old URLs after a rename, so the code changes work both before and after.

## PR Structure

Single PR with all code changes.

### Files to Modify

**Configuration:**

- `pyproject.toml` — Homepage/Download URLs
- `docs/source/conf.py` — github_repo, icon_links, PyPI URL

**Documentation:**

- `README.rst` — GitHub badges, PyPI badges, conda-forge badges, URLs
- `CONTRIBUTING.rst` — clone URLs, PyPI link, image URLs
- `docs/source/index.rst` — image URLs
- `docs/source/start/index.rst` — image URLs
- `docs/source/start/installation.rst` — GitHub URLs, clone commands
- `docs/source/tutorials/solara.rst` — clone URL
- `docs/source/tutorials/send-to-sepal.rst` — GitHub URLs
- `docs/source/tutorials/send-to-heroku.rst` — GitHub URLs
- `docs/source/tutorials/create-module.rst` — template repo URL

**Templates:**

- `pysepal/templates/map_app/ui.ipynb` — code_link, wiki_link, issue_link
- `pysepal/templates/panel_app/ui.ipynb` — code_link, wiki_link, issue_link
- `pysepal/templates/map_app/doc/en.rst` — issue URL
- `pysepal/templates/panel_app/doc/en.rst` — issue URL

**Python source (docstrings/comments/print statements):**

- `pysepal/bin/module_deploy.py` — docstrings, print statements
- `pysepal/bin/module_l10n.py` — docstrings, print statement
- `pysepal/bin/module_theme.py` — docstrings, print statements
- `pysepal/bin/module_factory.py` — GitHub URL in template generation
- `pysepal/planetapi/__init__.py` — package docstring
- `pysepal/mapping/__init__.py` — package docstring
- `pysepal/aoi/__init__.py` — package docstring
- `pysepal/sepalwidgets/__init__.py` — package docstring
- `pysepal/scripts/__init__.py` — package docstring
- `pysepal/message/__init__.py` — package docstring
- `pysepal/frontend/styles.py` — docstrings

**CSS (issue reference comments):**

- `pysepal/frontend/css/custom.css` — issue URL in comment
- `pysepal/solara/common/assets/custom.css` — issue URL in comment

## External Platform Actions (Post-Merge)

### 1. GitHub Repo Rename

1. Go to `github.com/openforis/sepal_ui` → Settings → General
2. Change repository name to `pysepal`
3. GitHub automatically creates a redirect from `openforis/sepal_ui` → `openforis/pysepal`
4. Update local git remote: `git remote set-url origin git@github.com:openforis/pysepal.git`

### 2. PyPI

The distribution name is already `pysepal` in `pyproject.toml` (changed in Phase 2). On next release (v3.4.0+), `twine upload` or CI publish will create the `pysepal` package on PyPI automatically.

Consider:

- Register `pysepal` on PyPI with a test upload if not already done
- Add a final `sepal-ui` release that depends on `pysepal` (redirect package) — or just let users follow the deprecation warning

### 3. Conda-Forge

1. Submit a PR to the `sepal-ui-feedstock` repo to rename the package
2. Or create a new `pysepal-feedstock` and archive the old one
3. Update the recipe to use the new PyPI package name

### 4. New Issues to Create

- **RTD migration**: Move ReadTheDocs project from `sepal-ui` to `pysepal`
- **Config file deprecation**: Deprecate `~/.sepal-ui-config` in favor of browser-based storage (Solara)

## Validation

After all changes:

- `rg "12rambau/sepal_ui"` — should match only in CHANGELOG.md, docs/plans/, and the shim
- `rg "openforis/sepal_ui"` — should match only in CHANGELOG.md, docs/plans/, and the shim
- `rg "pypi.org/project/sepal-ui"` — no matches outside docs/plans/
- `rg "conda-forge/sepal-ui"` — no matches outside docs/plans/
- All tests pass (`nox -s test`)
- Docs build passes (`nox -s docs`)
