import time

import ee

from sepal_ui.message import ms
from sepal_ui.scripts import utils as su


@su.need_ee
def wait_for_completion(task_descripsion, widget_alert=None):
    """
    Wait until the selected process is finished. Display some output information

    Args:
        task_descripsion (str): name of the running task
        widget_alert (v.Alert, optional): alert to display the output messages

    Return:
        (str): the final state of the task
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


@su.need_ee
def is_task(task_descripsion):
    """
    Search for the described task in the user Task list return None if nothing is found

    Args:
        task_descripsion (str): the task description

    Return:
        (ee.Task) : return the found task else None
    """

    current_task = None
    for task in ee.batch.Task.list():
        if task.config["description"] == task_descripsion:
            current_task = task
            break

    return current_task


@su.need_ee
def is_running(task_descripsion):
    """
    Search for the described task in the user Task list return None if nothing is currently running

    Args:
        task_descripsion (str): the task description

    Return:
        (ee.Task) : return the found task else None
    """

    current_task = is_task(task_descripsion)
    if current_task:
        if current_task.state not in ["RUNNING", "READY"]:
            current_task = None

    return current_task


@su.need_ee
def get_assets(folder=None, asset_list=[]):
    """
    Get all the assets from the parameter folder. every nested asset will be displayed.

    Args:
        folder (str): the initial GEE folder
        asset_list ([assets]| optional): extra element that you would like to add to the asset list

    Return:
        ([asset]): the asset list. each asset is a dict with 3 keys: 'type', 'name' and 'id'
    """
    # set the folder
    folder = folder if folder else ee.data.getAssetRoots()[0]["id"]

    # loop in the assets
    for asset in ee.data.listAssets({"parent": folder})["assets"]:
        if asset["type"] == "FOLDER":
            asset_list += [asset]
            asset_list = get_assets(asset["name"], asset_list)
        else:
            asset_list += [asset]

    return asset_list


@su.need_ee
def is_asset(asset_name, folder=None):
    """
    Check if the asset already exist in the user asset folder

    Args:
        asset_descripsion (str) : the descripsion of the asset
        folder (str): the folder of the glad assets

    Return:
        (bool): true if already in folder
    """

    # get the folder
    folder = folder or ee.data.getAssetRoots()[0]["id"]

    # get all the assets
    asset_list = get_assets(folder)

    # search for asset existance
    exist = False
    for asset in asset_list:
        if asset_name == asset["name"]:
            exist = True
            break

    return exist
