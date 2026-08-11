"""Local-development login for pysepal Solara apps.

``PYSEPAL_DEV_AUTH`` exists so a developer can run an app against a real SEPAL
instance from a laptop, where no SEPAL proxy injects headers. It is a single
process-wide identity by design and it is unreachable in a real container,
where validated SEPAL headers take precedence over it (see
:func:`pysepal.solara._topology.resolve_session_plan`).
"""

import logging
import os
import threading
from typing import Optional

from eeclient.helpers import get_sepal_headers_from_auth
from eeclient.models import SepalHeaders

from pysepal.solara._topology import DEV_AUTH_ENV_VAR, dev_auth_enabled

logger = logging.getLogger("sepalui.solara.dev_auth")

__all__ = ["prime_dev_auth"]

_dev_headers: Optional[SepalHeaders] = None
_lock = threading.Lock()


def prime_dev_auth() -> SepalHeaders:
    """Log in once for the whole process with the developer credentials.

    ``get_sepal_headers_from_auth`` issues a blocking HTTP POST against
    ``SEPAL_HOST`` with ``LOCAL_SEPAL_USER`` / ``LOCAL_SEPAL_PASSWORD``. Call
    this from application startup to keep that POST off the render path; the
    session layer otherwise calls it lazily on the first render.

    Returns:
        The developer's SEPAL headers, cached for the process.

    Raises:
        RuntimeError: ``PYSEPAL_DEV_AUTH`` is not armed.
        ValueError: The developer credential environment variables are unset.
    """
    global _dev_headers

    if not dev_auth_enabled(os.environ):
        raise RuntimeError(
            f"{DEV_AUTH_ENV_VAR} is not set; refusing to use a developer login. "
            "Arm it with 1 for local development only."
        )

    with _lock:
        if _dev_headers is None:
            logger.info("Logging in with the local development credentials")
            _dev_headers = get_sepal_headers_from_auth()
        return _dev_headers


def _reset_dev_auth_cache() -> None:
    """Drop the cached developer login (tests, and dev-server reloads)."""
    global _dev_headers

    with _lock:
        _dev_headers = None
