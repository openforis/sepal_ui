"""Bootstrap for the *global* ``ee`` module.

Two functions, both about the same thing: making ``ee.Initialize()`` have
happened. :func:`init_ee` runs it from the machine's own credentials, and
:func:`need_ee` guards code that would otherwise raise ``EEException: client
library not initialized``. Building an Earth Engine graph -- ``ee.Image(...)``,
``ee.FeatureCollection(...)`` -- is client-side and needs this, whoever
initialised it.

Nothing here is session-aware, so nothing that *executes* belongs here.
``getInfo``, ``getMapId``, exports, and listing, inspecting or deleting assets
spend a quota and touch private data. They go through the connection's own
session: ``get_current_gee_interface()`` and the ``GEEInterface`` methods.

4.0 removed the asset and task helpers this module used to carry. They ran
against the global ``ee``, which in an app-launcher container is the platform
service account, so they answered for the wrong identity without erroring --
and one of them deleted. ``docs/guides/migration-v4.md`` names the replacement
for each.

``init_ee`` is the gap that remains: it accepts the service-account key the
session layer refuses two layers up, which ``pysepal/solara/_topology.py``
describes.
"""

import json
import os
from functools import wraps
from pathlib import Path
from typing import Any, Callable

import ee
from deprecated.sphinx import versionadded


@versionadded(version="3.0", reason="moved from utils to a dedicated module")
def need_ee(func: Callable) -> Any:
    """Decorator to execute check if the object require EE binding.

    Trigger an exception if the connection is not possible.

    Args:
        func: the object on which the decorator is applied

    Returns:
        The return statement of the decorated method
    """

    @wraps(func)
    def wrapper_ee(*args, **kwargs):
        # init_ee() is best-effort and no-ops without credentials, so require an
        # initialized session here rather than trusting the call to have raised
        try:
            init_ee()
        except Exception:
            pass

        if not ee.data.is_initialized():
            raise Exception("This function needs an Earth Engine authentication")

        return func(*args, **kwargs)

    return wrapper_ee


def init_ee() -> None:
    r"""Initialize earth engine according using a token.

    THe environment used to run the tests need to have a EARTHENGINE_TOKEN variable.
    The content of this variable must be the copy of a personal credential file that you can find on your local computer if you already run the earth engine command line tool. See the usage question for a github action example.

    - Windows: ``C:\Users\USERNAME\\.config\\earthengine\\credentials``
    - Linux: ``/home/USERNAME/.config/earthengine/credentials``
    - MacOS: ``/Users/USERNAME/.config/earthengine/credentials``

    Note:
        As all init method of pytest-gee, this method will fallback to a regular ``ee.Initialize()`` if the environment variable is not found e.g. on your local computer.
    """
    if not ee.data.is_initialized():
        credential_folder_path = Path.home() / ".config" / "earthengine"
        credential_file_path = credential_folder_path / "credentials"

        ee_token = os.environ.get("EARTHENGINE_TOKEN")
        if ee_token and not credential_file_path.exists():

            # write the token to the appropriate folder
            credential_folder_path.mkdir(parents=True, exist_ok=True)
            credential_file_path.write_text(ee_token)

        if not credential_file_path.exists():
            return

        # Extract the project name from credentials
        _credentials = json.loads(credential_file_path.read_text())
        project_id = _credentials.get("project_id", _credentials.get("project", None))

        if not project_id:
            raise NameError(
                "The project name cannot be detected. "
                "Please set it using `earthengine set_project project_name`."
            )

        # Check if we are using a google service account
        if _credentials.get("type") == "service_account":
            ee_user = _credentials.get("client_email")
            credentials = ee.ServiceAccountCredentials(ee_user, str(credential_file_path))
            ee.Initialize(credentials=credentials, project=project_id)
            return

        # if the user is in local development the authentication should
        # already be available
        ee.Initialize(project=project_id)
