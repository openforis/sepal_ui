"""Compatibility shim for `pysepal.scripts.sepal_client`.

Re-exports `pysepal_api.compat.SepalClient`, which is a drop-in replacement
for the legacy v3 class (same constructor, same method names, same returned
shapes, same public attributes). A deprecation warning fires when callers
construct the class so import-time noise stays out of pysepal's
module-loading path.

This shim is scheduled for removal in pysepal v4.
"""

from pysepal_api.compat import SepalClient

__all__ = ["SepalClient"]
