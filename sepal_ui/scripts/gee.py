"""All the heleper methods to interface Google Earthengine with sepal-ui."""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Union

import ee
import ipyvuetify as v
from deprecated.sphinx import deprecated

from sepal_ui.message import ms
from sepal_ui.scripts import decorator as sd


@sd.need_ee
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


@sd.need_ee
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


@sd.need_ee
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
    reason="This function is no longer required. Use GEEInterface.get_assets() instead for better performance and resource management.",
    version="3.2.0",
    category=DeprecationWarning,
)
async def _list_assets_concurrent(folders: list, semaphore: asyncio.Semaphore) -> list:
    """List assets concurrently using ThreadPoolExecutor.

    .. deprecated:: 3.2.0
        This function is deprecated. Use GEEInterface.get_assets() instead.

    Args:
        folders: list of folders to list assets from

    Returns:
        list of assets for each folder
    """
    async with semaphore:
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_running_loop()
            tasks = [
                loop.run_in_executor(executor, ee.data.listAssets, {"parent": folder})
                for folder in folders
            ]
            results = await asyncio.gather(*tasks)
            return results


# Deprecated alias - use GEEInterface.get_assets() instead
list_assets_concurrent = _list_assets_concurrent


@deprecated(
    reason="Use GEEInterface.get_assets() instead for better performance and resource management.",
    version="3.2.0",
    category=DeprecationWarning,
)
async def get_assets_async_concurrent(folder: str, gee_interface=None) -> List[dict]:
    """Get all the assets from the parameter folder. every nested asset will be displayed.

    .. deprecated:: 3.2.0
        This function is deprecated. Use GEEInterface.get_assets() instead.

    Args:
        folder: the initial GEE folder

    Returns:
        the asset list. each asset is a dict with 3 keys: 'type', 'name' and 'id'

    """
    if not gee_interface:
        from sepal_ui.scripts.gee_interface import GEEInterface

        gee_interface = GEEInterface()

    return await gee_interface.get_assets_async(folder)


@deprecated(
    reason="Use GEEInterface.get_assets() instead for better performance and resource management.",
    version="3.2.0",
    category=DeprecationWarning,
)
@sd.need_ee
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
    folder = str(folder) or f"projects/{ee.data._cloud_api_user_project}/assets/"

    return _get_assets_sync(folder)


@sd.need_ee
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


@deprecated(
    reason="Use GEEInterface.get_asset() with not_exists_ok=True instead. "
    "The 'asset_name' and 'folder' parameters are deprecated. Use 'asset_id' directly.",
    version="3.2.0",
    category=DeprecationWarning,
)
@sd.need_ee
def is_asset(asset_name: str = None, folder: Union[str, Path] = "", asset_id: str = None) -> bool:
    """Check if the asset already exist in the user asset folder.

    Args:
        asset_name: [DEPRECATED] the name of the asset (use asset_id instead)
        folder: [DEPRECATED] the folder of the assets (use full asset_id instead)
        asset_id: the complete asset ID (e.g., 'projects/your-project/assets/folder/asset_name')

    Returns:
        true if asset exists, false otherwise
    """
    # Handle backward compatibility
    if asset_id is None:
        if asset_name is None:
            raise ValueError("Either 'asset_id' or 'asset_name' must be provided")

        # Check if asset_name already contains the full path
        if asset_name.startswith("projects/"):
            asset_id = asset_name
        else:
            # Construct asset_id from legacy parameters
            folder = str(folder)
            if folder and not folder.startswith("projects/"):
                # If folder doesn't start with 'projects/', assume it's a relative path
                folder = f"projects/{ee.data._cloud_api_user_project}/assets/{folder}"
            elif not folder:
                # If no folder provided, use default
                folder = f"projects/{ee.data._cloud_api_user_project}/assets/"

            # Ensure folder ends with '/' for proper concatenation
            if not folder.endswith("/"):
                folder += "/"
            asset_id = folder + asset_name

    # Use GEEInterface to check if asset exists
    from sepal_ui.scripts.gee_interface import GEEInterface

    with GEEInterface() as gee_interface:
        result = gee_interface.get_asset(asset_id, not_exists_ok=True)
        return result is not None


@sd.need_ee
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
