"""All the heleper methods to interface Google Earthengine with sepal-ui."""

import time
from pathlib import Path
from typing import List, Union

import ee
import ipyvuetify as v

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


@sd.need_ee
def get_assets(folder: Union[str, Path] = "", asset_list: List[str] = []) -> List[str]:
    """Get all the assets from the parameter folder. every nested asset will be displayed.

    Args:
        folder: the initial GEE folder
        asset_list: extra element that you would like to add to the asset list

    Returns:
        the asset list. each asset is a dict with 3 keys: 'type', 'name' and 'id'
    """
    # set the folder
    folder = str(folder) or ee.data.getAssetRoots()[0]["id"]

    # loop in the assets
    for asset in ee.data.listAssets({"parent": folder})["assets"]:
        if asset["type"] == "FOLDER":
            asset_list += [asset]
            asset_list = get_assets(asset["name"], asset_list)
        else:
            asset_list += [asset]

    return asset_list


@sd.need_ee
def is_asset(asset_name: str, folder: Union[str, Path] = "") -> bool:
    """Check if the asset already exist in the user asset folder.

    Args:
        asset_descripsion: the descripsion of the asset
        folder: the folder of the glad assets

    Returns:
        true if already in folder
    """
    # get the folder
    folder = str(folder) or ee.data.getAssetRoots()[0]["id"]

    # get all the assets
    asset_list = get_assets(folder)

    # search for asset existance
    exist = False
    for asset in asset_list:
        if asset_name == asset["name"]:
            exist = True
            break

    return exist
