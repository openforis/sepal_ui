"""Resolve module names against this checkout only.

A developer machine often has another pysepal on the path -- an editable
install of a sibling clone, say -- so a retired name resolving *somewhere*
says nothing about what this tree ships. Every helper here answers the only
question worth asking: does this checkout still provide it?
"""

import importlib.util
import site
import sys
import sysconfig
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1].resolve()

OUR_TOP_LEVEL = frozenset({"pysepal", "sepal_ui"})
"Distributions this checkout is answerable for, wherever they are installed."


def _site_package_roots() -> tuple[Path, ...]:
    """Return the interpreter's installed-package directories.

    ``nox`` builds its virtualenv at ``.nox/`` *inside* the checkout, so every
    third-party package it installs sits under :data:`REPO_ROOT`. Without this,
    ``pytest``'s own import hook counts as pysepal's code.
    """
    paths = [sysconfig.get_paths().get(key) for key in ("purelib", "platlib")]
    paths += site.getsitepackages() if hasattr(site, "getsitepackages") else []
    paths.append(site.getusersitepackages() if hasattr(site, "getusersitepackages") else None)
    return tuple({Path(path).resolve() for path in paths if path})


_SITE_PACKAGE_ROOTS = _site_package_roots()


def shipped_locations(module: str) -> list[Path]:
    """Return the paths inside this checkout that would provide ``module``.

    Both halves of the spec matter. A regular module is described by
    ``origin``; a namespace package -- a directory with no ``__init__.py`` --
    has no origin at all and carries its directories in
    ``submodule_search_locations`` instead. Reading only ``origin`` would let
    ``sepal_ui/legacy.py`` reappear without a single test noticing.

    Args:
        module: Dotted module name, resolved without importing it.

    Returns:
        The matching paths under ``REPO_ROOT``; empty when this checkout does
        not provide the name.
    """
    try:
        spec = importlib.util.find_spec(module)
    except (ImportError, AttributeError, ValueError):
        return []
    if spec is None:
        return []
    found = [Path(spec.origin)] if spec.origin else []
    found += [Path(location) for location in spec.submodule_search_locations or ()]
    return [path for path in found if path.is_relative_to(REPO_ROOT)]


def defined_in_repo(obj: object) -> bool:
    """Say whether ``obj``'s class is defined by code this checkout answers for.

    Being under :data:`REPO_ROOT` is not enough on its own: an in-tree
    virtualenv puts every installed dependency there too. Code inside one counts
    only when it belongs to a distribution in :data:`OUR_TOP_LEVEL`, so a shim
    that returns in an *installed* pysepal is still caught.

    Args:
        obj: Any object; the lookup is on its type's defining module.

    Returns:
        True when that module's file is this checkout's own code.
    """
    module = sys.modules.get(type(obj).__module__)
    origin = getattr(module, "__file__", None)
    if origin is None:
        return False

    path = Path(origin).resolve()
    if not path.is_relative_to(REPO_ROOT):
        return False

    for root in _SITE_PACKAGE_ROOTS:
        if path.is_relative_to(root):
            return path.relative_to(root).parts[0] in OUR_TOP_LEVEL
    return True
