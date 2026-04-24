"""Backward-compatibility shim: redirects all sepal_ui imports to pysepal.

This package is deprecated. Use ``import pysepal`` instead.
"""

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
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

    _active = set()

    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith("sepal_ui."):
            return None
        # Prevent re-entrant calls while resolving the same name
        if fullname in self._active:
            return None
        self._active.add(fullname)
        try:
            new_name = fullname.replace("sepal_ui", "pysepal", 1)
            spec = importlib.util.find_spec(new_name)
            if spec is None:
                return None
            # Create a spec that loads the pysepal module but registers under sepal_ui name
            return importlib.machinery.ModuleSpec(
                fullname,
                _SepalUiLoader(new_name),
                origin=spec.origin,
                is_package=spec.submodule_search_locations is not None,
            )
        finally:
            self._active.discard(fullname)


class _SepalUiLoader(importlib.abc.Loader):
    """Load pysepal module and alias it under sepal_ui name."""

    def __init__(self, real_name):
        self._real_name = real_name

    def create_module(self, spec):
        return None  # use default module creation

    def exec_module(self, module):
        real_mod = importlib.import_module(self._real_name)
        # Replace the module in sys.modules with the real one
        sys.modules[module.__name__] = real_mod
        module.__dict__.update(real_mod.__dict__)


sys.meta_path.insert(0, _SepalUiFinder())


def __getattr__(name):
    """Lazily forward attribute access to pysepal to avoid circular imports."""
    import pysepal

    try:
        return getattr(pysepal, name)
    except AttributeError:
        raise AttributeError(f"module 'sepal_ui' has no attribute {name!r}")
