# Phase 2 Design: Mechanical Rename `sepal_ui` → `pysepal`

## Context

Phase 1 (deprecation warnings) shipped in v3.2.0 on Feb 2026. Users importing `sepal_ui` see a `DeprecationWarning` pointing them to plan migration to `pysepal`. This document covers Phase 2: the mechanical rename.

Reference: `.plans/issue-967-rename-plan.md`

## Scope

### Renamed in Phase 2

| Category                             | Before                          | After                |
| ------------------------------------ | ------------------------------- | -------------------- |
| Source directory                     | `sepal_ui/`                     | `pysepal/`           |
| Distribution name (`pyproject.toml`) | `sepal-ui`                      | `pysepal`            |
| All internal Python imports          | `from sepal_ui.*`               | `from pysepal.*`     |
| All test imports                     | `from sepal_ui.*`               | `from pysepal.*`     |
| Entry points/scripts                 | `sepal_ui.bin.*`                | `pysepal.bin.*`      |
| `pyproject.toml` tool config paths   | coverage, codespell, commitizen | updated to `pysepal` |
| `noxfile.py` paths                   | `"sepal_ui"`                    | `"pysepal"`          |
| `.readthedocs.yaml`                  | `./sepal_ui`                    | `./pysepal`          |
| CI workflow paths                    | `.github/workflows/`            | updated paths        |
| Tracked notebooks                    | 7 `.ipynb` files                | updated imports      |
| Template Python files                | `sepal_ui` imports              | `pysepal` imports    |
| Template `requirements.txt`          | `sepal_ui`                      | `pysepal`            |
| Docs config and module RST files     | `sepal_ui` references           | `pysepal`            |

### NOT Renamed in Phase 2 (deferred or permanent)

| Item                                                | Reason                                               |
| --------------------------------------------------- | ---------------------------------------------------- |
| `~/.sepal-ui-config` file path                      | Would break user settings on disk                    |
| `[sepal-ui]` ConfigParser section name              | Would break user settings; dual-read added instead   |
| `sepalui` logger namespace                          | Would break downstream logging config                |
| `sepal-ui-script` CSS class                         | DOM-level, no user benefit to rename                 |
| `[sepal-ui]` section in downstream `pyproject.toml` | Tools will read both section names during transition |
| GitHub repo URL/org                                 | Phase 3                                              |

## Compatibility Shim

### Import Redirection

A thin `sepal_ui/` directory lives alongside `pysepal/` in the repo root. It contains an `__init__.py` that:

1. Emits a `DeprecationWarning` on import
2. Uses `sys.modules` manipulation and a custom `importlib.abc.MetaPathFinder` to transparently redirect all `sepal_ui.*` imports to `pysepal.*`
3. Handles `from sepal_ui.X import Y` patterns

The `pyproject.toml` packages config includes both `pysepal` and the thin `sepal_ui` shim, so `pip install pysepal` installs both import paths.

### Config Section Dual-Read

`pysepal/conf.py` reads `[pysepal]` first, falls back to `[sepal-ui]`. Same dual-read logic in `module_deploy` and `module_venv` when reading downstream `pyproject.toml` files.

### Template Scaffolding

New modules created by `module_factory` use `pysepal` imports and `[pysepal]` config section. Existing modules continue to work via the shim + dual-read.

## PR Breakdown

### PR B1: Directory Rename + Packaging + Shim

- Rename `sepal_ui/` → `pysepal/`
- Create thin `sepal_ui/` shim directory with `__init__.py` and `MetaPathFinder`
- Update `pyproject.toml`: name, packages, scripts, tool config paths
- Update `noxfile.py`, `.readthedocs.yaml`, CI workflow paths
- Add dual-read logic to `pysepal/conf.py` for `[sepal-ui]`/`[pysepal]` sections
- Tests may not all pass yet (internal imports still say `sepal_ui`)

### PR B2: Internal Import Rename

- Mechanical find-and-replace: `from sepal_ui.` → `from pysepal.` and `import sepal_ui.` → `import pysepal.` across all `.py` files in `pysepal/` and `tests/`
- Update `docs/source/conf.py` and `docs/source/modules/*.rst`
- All tests should pass after this PR

### PR B3: Notebooks + Templates + Docs Cleanup

- Update all 7 tracked `.ipynb` files
- Update template `requirements.txt`, `pyproject.toml` sections, and Python files
- Update all doc import examples and references
- Clean up stale `build/` directory
- Final validation: `rg "\bsepal_ui\b"` should only match the shim and intentional deprecation mentions

## Validation Checklist

After all three PRs are merged:

- [ ] `import pysepal` works for all documented entry paths
- [ ] `import sepal_ui` still works with deprecation warning (via shim)
- [ ] `from sepal_ui.sepalwidgets import AppBar` works (shim submodule redirect)
- [ ] `rg -n "\bsepal_ui\b" --glob '!*.ipynb'` only matches shim and migration docs
- [ ] `rg -n "\bsepal_ui\b" --type ipynb` shows no stale references in notebooks
- [ ] Unit tests pass (`nox -s test`)
- [ ] Notebook tests pass (`pytest --nbmake`)
- [ ] Docs build passes
- [ ] `module_factory` creates new modules with `pysepal` imports
- [ ] `module_deploy` works with both `[sepal-ui]` and `[pysepal]` sections
- [ ] `~/.sepal-ui-config` is still read correctly (unchanged)
- [ ] Logger namespace `sepalui.*` is unchanged

## Risks and Mitigations

| Risk                                                     | Mitigation                                                                        |
| -------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Shim `MetaPathFinder` doesn't handle all import patterns | Thorough test coverage of shim with various import styles                         |
| Downstream modules break on `[sepal-ui]` section         | Dual-read logic accepts both section names                                        |
| CI breaks during PR B1 (before imports are renamed)      | Expected; PR B2 fixes imports                                                     |
| Stale `sepal_ui` references missed                       | Automated grep validation in PR B3                                                |
| `pip install sepal-ui` stops updating                    | Same-repo shim ensures both import paths are installed with `pip install pysepal` |

## Timeline

- PR B1: First week
- PR B2: Second week (after B1 is reviewed/merged)
- PR B3: Third week (after B2 is reviewed/merged)
