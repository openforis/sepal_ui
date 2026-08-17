"""All the helper methods to interface Google Earth Engine with pysepal.

.. warning::

   **Modules should not call the asset helpers here.** ``get_ee_project``
   (``ee.data.getProjectConfig``), ``get_assets`` (``ee.data.listAssets``) and
   ``delete_assets`` (``ee.data.getAsset``, ``ee.data.deleteAsset``) execute
   against the *global* ``ee`` module, which answers as whatever identity
   ``ee.Initialize()`` was given. In an app-launcher container that is the
   platform service account, so they list, inspect and *delete* against the
   platform's asset tree rather than the user's, with no error to show for it.

   Use the session-bound interface instead: ``get_current_gee_interface()``
   returns one built from the connection's own credentials, and
   ``GEEInterface.get_assets``, ``get_assets_async``, ``get_asset`` and
   ``get_folder`` are the equivalents.

   ``GEEInterface`` no longer falls through to any of them -- since 4.0 every one
   of its methods goes through the session. What keeps them alive is
   ``delete_assets``, which backs the test-suite teardown and the
   ``clean_gee_assets`` janitor and reaches ``get_assets`` (and through it
   ``get_ee_project``) to walk a folder before deleting it. Those run as their
   own identity, in a runtime that owns its credentials, which is the only
   context any of this is correct in.

   They remain for notebooks, scripts and the SEPAL sandbox, where the machine's
   credentials are the one user's own and the global ``ee`` is the right answer.

Splitting the two halves is worth stating plainly, because they are not the same
problem. *Building* an Earth Engine graph -- ``ee.Image(...)``,
``ee.FeatureCollection(...)`` -- is client-side and moves no user data, so it
needs ``ee.Initialize()`` to have run but does not care whose credentials did it.
*Executing* -- ``getInfo``, ``getMapId``, exports, asset listing -- is what
spends a quota, reads private assets and writes to a Drive, and in a multi-user
process it must go through the connection's own session. The functions above are
the second kind wearing the clothes of the first.
"""

import json
import os
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List, Union

import ee
import ipyvuetify as v
from deprecated.sphinx import deprecated, versionadded

from pysepal.message import ms


def get_ee_project() -> str:
    """Get the current Earth Engine project ID.

    Returns:
        The project ID (e.g., 'ee-username').
    """
    if not ee.data.is_initialized():
        raise RuntimeError("Earth Engine is not initialized. Call init_ee() first.")

    config = ee.data.getProjectConfig()
    # Extract project ID from 'projects/PROJECT_ID/config' format
    return config["name"].split("/")[1]


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


@need_ee
def wait_for_completion(task_descripsion: str, widget_alert: v.Alert = None) -> str:
    """Wait until the selected process is finished. Display some output information.

    Args:
        task_descripsion: name of the running task
        widget_alert: alert to display the output messages

    Returns:
        the final state of the task
    """
    state = "UNSUBMITTED"
    while state != "COMPLETED":

        # print in a widget
        if widget_alert:
            widget_alert.add_live_msg(ms.status.format(state))

        # wait 5 seconds
        time.sleep(5)

        # search for the task in task_list
        current_task = is_task(task_descripsion)
        state = current_task.state

        if state == "FAILED":
            raise Exception(ms.status.format(state))

    # print in a widget
    if widget_alert:
        widget_alert.add_live_msg(ms.status.format(state), "success")

    return state


@need_ee
def is_task(task_descripsion: str) -> ee.batch.Task:
    """Search for the described task in the user Task list return None if nothing is found.

    Args:
        task_descripsion: the task description

    Returns:
        return the found task else None
    """
    current_task = None
    for task in ee.batch.Task.list():
        if task.config["description"] == task_descripsion:
            current_task = task
            break

    return current_task


@need_ee
def is_running(task_descripsion: str) -> ee.batch.Task:
    """Search for the described task in the user Task list return None if nothing is currently running.

    Args:
        task_descripsion: the task description

    Returns:
        return the found task else None
    """
    current_task = is_task(task_descripsion)
    if current_task:
        if current_task.state not in ["RUNNING", "READY"]:
            current_task = None

    return current_task


@deprecated(
    reason="Use GEEInterface.get_assets() instead for better performance and resource management.",
    version="3.2.0",
    category=DeprecationWarning,
)
@need_ee
def _get_assets(folder: Union[str, Path] = "", async_=True) -> List[dict]:
    """Get all the assets from the parameter folder. every nested asset will be displayed.

    .. deprecated:: 3.2.0
        This function is deprecated. Use GEEInterface.get_assets() instead.

    Args:
        folder: the initial GEE folder
        async_: whether or not the function should be executed asynchronously

    Returns:
        the asset list. each asset is a dict with 3 keys: 'type', 'name' and 'id'

    """
    folder = str(folder) if folder else f"projects/{get_ee_project()}/assets/"

    return _get_assets_sync(folder)


@need_ee
def _get_assets_sync(folder: Union[str, Path] = "") -> List[dict]:
    """Get all the assets from the parameter folder. every nested asset will be displayed.

    Args:
        folder: the initial GEE folder

    Returns:
        the asset list. each asset is a dict with 3 keys: 'type', 'name' and 'id'
    """
    # set the folder and init the list
    asset_list = []

    def _recursive_get(folder, asset_list):

        # loop in the assets
        for asset in ee.data.listAssets({"parent": folder})["assets"]:
            asset_list += [asset]
            if asset["type"] == "FOLDER":
                asset_list = _recursive_get(asset["name"], asset_list)

        return asset_list

    return _recursive_get(folder, asset_list)


# Deprecated alias - use GEEInterface.get_assets() instead
get_assets = _get_assets


@need_ee
def delete_assets(asset_id: str, dry_run: bool = True) -> None:
    """Delete the selected asset and all its content.

    This method will delete all the files and folders existing in an asset folder. By default a dry run will be launched and if you are satisfyed with the displayed names, change the ``dry_run`` variable to ``False``. No other warnng will be displayed.

    .. warning::

        If this method is used on the root directory you will loose all your data, it's highly recommended to use a dry run first and carefully review the destroyed files.

    Args:
        asset_id: the Id of the asset or a folder
        dry_run: whether or not a dry run should be launched. dry run will only display the files name without deleting them.
    """
    # define the action to execute for each asset based on the dry run mode
    def delete(id: str) -> None:
        if dry_run is True:
            print(f"to be deleted: {id}")
        else:
            print(f"deleting: {id}")
            ee.data.deleteAsset(id)

        return

    # identify the type of asset
    asset_info = ee.data.getAsset(asset_id)

    if asset_info["type"] == "FOLDER":

        # get all the assets
        asset_list = get_assets(folder=asset_id)

        # split the files by nesting levels
        # we will need to delete the more nested files first
        assets_ordered = {}
        for asset in asset_list:
            lvl = len(asset["id"].split("/"))
            assets_ordered.setdefault(lvl, [])
            assets_ordered[lvl].append(asset)

        # delete all items starting from the more nested one but not folders
        assets_ordered = dict(sorted(assets_ordered.items(), reverse=True))
        for lvl in assets_ordered:
            for i in assets_ordered[lvl]:
                delete(i["name"])

    # delete the initial folder/asset
    delete(asset_id)

    return


@need_ee
def get_task(task_id):
    """Get task."""
    tasks_list = ee.batch.Task.list()
    for task in tasks_list:
        if task.id == task_id:
            return task

    raise Exception(f"The task id {task_id} doesn't exist in your tasks.")


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
