"""Temporary directories that land on local disk.

On a SEPAL sandbox ``$TMPDIR`` is unset and ``/tmp`` is nfs4 under the user's home
export, so ``tempfile.mkdtemp()`` writes to a network filesystem and against the
storage quota. ``/var/tmp`` is container-local and wiped with the session.
"""

import os
import tempfile
from pathlib import Path

SEPAL_SCRATCH_DIR = Path("/var/tmp")


def on_sepal() -> bool:
    """Whether this process runs inside a SEPAL sandbox, which exports ``SEPAL=true``."""
    return os.environ.get("SEPAL", "").strip().lower() == "true"


def scratch_root() -> Path:
    """Local disk on SEPAL, the stdlib temp dir anywhere else.

    Falls back to the stdlib default when the SEPAL path is unusable, so a slow
    write never becomes a failed one.
    """
    if on_sepal() and os.access(SEPAL_SCRATCH_DIR, os.W_OK):
        return SEPAL_SCRATCH_DIR

    return Path(tempfile.gettempdir())


def scratch_dir(prefix: str = "sepal_ui_") -> Path:
    """Create a new temporary directory under :func:`scratch_root`; the caller owns cleanup."""
    root = scratch_root()
    root.mkdir(parents=True, exist_ok=True)

    return Path(tempfile.mkdtemp(prefix=prefix, dir=root))
