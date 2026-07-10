"""Deprecated compatibility shim for the pre-0.2 vendored SepalClient.

Temporary bridge so downstream apps that still import
``(sepal_ui|pysepal).scripts.sepal_client.SepalClient`` and call the legacy
file verbs keep working against pysepal >= 3.7. Scheduled for removal in
pysepal 4.0.

New code: ``from pysepal_api import SepalClient`` and use the ``.files.*`` API.
"""
from __future__ import annotations

import warnings
from pathlib import Path, PurePosixPath
from typing import Any, Optional, Sequence, Union

from pysepal_api import SepalClient as _ApiSepalClient

__all__ = ["SepalClient"]

_REMOVED_IN = "pysepal 4.0"


class SepalClient(_ApiSepalClient):
    """``pysepal_api.SepalClient`` plus the three legacy file verbs.

    Each legacy verb delegates to ``self.files.*`` and emits a ``DeprecationWarning``.
    """

    def get_remote_dir(self, folder: Union[str, Path], parents: bool = False) -> PurePosixPath:
        """Create a remote directory (deprecated; use files.mkdir instead)."""
        warnings.warn(
            f"SepalClient.get_remote_dir() is deprecated and will be removed in "
            f"{_REMOVED_IN}; use SepalClient.files.mkdir() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.files.mkdir(str(folder), parents=parents)

    def set_file(
        self, file_path: str, content: Union[str, bytes], overwrite: bool = False
    ) -> dict[str, Any]:
        """Write a file to the remote (deprecated; use files.write instead)."""
        warnings.warn(
            f"SepalClient.set_file() is deprecated and will be removed in "
            f"{_REMOVED_IN}; use SepalClient.files.write() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.files.write(file_path, content, overwrite=overwrite).model_dump()

    def list_files(
        self, folder: str = "/", extensions: Optional[Sequence[str]] = None
    ) -> dict[str, Any]:
        """List files in a remote folder (deprecated; use files.list instead)."""
        warnings.warn(
            f"SepalClient.list_files() is deprecated and will be removed in "
            f"{_REMOVED_IN}; use SepalClient.files.list() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.files.list(folder, extensions=extensions).model_dump()
