"""Resolve module names against this checkout only.

A developer machine often has another pysepal on the path -- an editable
install of a sibling clone, say -- so a retired name resolving *somewhere*
says nothing about what this tree ships. Every helper here answers the only
question worth asking: does this checkout still provide it?
"""

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]


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
    """Say whether ``obj``'s class is defined by code in this checkout.

    Args:
        obj: Any object; the lookup is on its type's defining module.

    Returns:
        True when that module has a file under ``REPO_ROOT``.
    """
    module = sys.modules.get(type(obj).__module__)
    origin = getattr(module, "__file__", None)
    return origin is not None and Path(origin).is_relative_to(REPO_ROOT)
