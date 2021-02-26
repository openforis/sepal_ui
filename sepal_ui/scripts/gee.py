import time

import ee

from sepal_ui.message import ms
from sepal_ui.scripts import utils as su
    
# initialize earth engine
su.init_ee()

def wait_for_completion(task_descripsion, widget_alert=None):
    """
    Wait until the selected process is finished. Display some output information

    Args:
        task_descripsion (str): name of the running task
        widget_alert (v.Alert, optional): alert to display the output messages
        
    Return:
        (str): the final state of the task
    """
    state = 'UNSUBMITTED'
    while state != 'COMPLETED':
        
        # print in a widget
        if widget_alert: 
            widget_alert.add_live_msg(ms.status.format(state))
            
        # wait 5 seconds
        time.sleep(5)
                    
        # search for the task in task_list
        current_task = isTask(task_descripsion)
        state = current_task.state
        
        if state == 'FAILED':
            raise Exception(ms.status.format(state))
        
    # print in a widget
    if widget_alert: 
        widget_alert.add_live_msg(ms.status.format(state), 'success')
        
    return state
        
def isTask(task_descripsion):
    """
    Search for the described task in the user Task list return None if nothing is find
    
    Args: 
        task_descripsion (str): the task description
    
    Return:
        (ee.Task) : return the found task else None
    """
    
    current_task = None
    for task in ee.batch.Task.list():
        if task.config['description'] == task_descripsion:
            current_task = task
            break
            
    return current_task


