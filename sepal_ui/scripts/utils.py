import time
from datetime import datetime
import os
import glob
from pathlib import Path
import csv
from urllib.parse import urlparse
import subprocess

import ipyvuetify as v


def displayIO(widget_alert, message, alert_type='info'):
    """ Display the message in a vuetify alert DOM object with specific coloring
    Args: 
        widget_alert (v.Alert) : the vuetify alert to modify
        alert_type (str) : the alert color
        message (v.Children) : a DOM element or a string to fill the message 
    """
    
    list_color = ['info', 'success', 'warning', 'error']
    if not alert_type in list_color:
        alert_type = 'info'
        
    widget_alert.type = alert_type
     
    current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
    widget_alert.children = [
        v.Html(tag='p', children=['[{0}]'.format(current_time)]),
        v.Html(tag='p', children=[message])
   ]
    
def toggleLoading(btn):
    """Toggle the loading state for a given btn in the ipyvutify lib
    
    Args:
        btn (v.Btn) : the btn to toggle
    """
    
    btn.loading = not btn.loading
    btn.disabled = btn.loading
    
def create_FIPS_dic():
    """create the list of the country code in the FIPS norm using the CSV file provided in utils
        
    Returns:
        fips_dic (dic): the country FIPS_codes labelled with english country names
    """
     
    pathname = os.path.join(os.path.dirname(__file__), 'FIPS_code_to_country.csv')
    fips_dic = {}
    with open(pathname, newline='') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        for row in reader:
            fips_dic[row[1]] = row[3]
            
        fips_sorted = {}
        for key in sorted(fips_dic):
            fips_sorted[key] = fips_dic[key]
        
    return fips_sorted

def get_shp_files():
    """return all the .shp files available in the user directories. Will verify if the .dbf and .shx exists and are located at the same place
    
    Returns: 
        shp_list (str[]): the path to every .shp complete and available, empty list if none
    """
    
    root_dir = os.path.expanduser('~')
    raw_list = glob.glob(root_dir + "/**/*.shp", recursive=True)
    
    #check if the file is complete
    shp_list = []
    for pathname in raw_list:
        path = Path(pathname)
        if os.path.isfile(path.with_suffix('.dbf')) and os.path.isfile(path.with_suffix('.shx')):
            shp_list.append(pathname)

    return shp_list

def create_download_link(pathname):
    """return a clickable link to download the pathname target"""
    
    result_path = os.path.expanduser(pathname)
    home_path = os.path.expanduser('~')
    download_path='/'+os.path.relpath(result_path,home_path)
    
    link = "/api/files/download?path={}".format(download_path)
    
    return link

def is_absolute(url):
    """ check if the given url is an absolute or relative path"""
    return bool(urlparse(url).netloc)

def launch(command, output=None):
    """launch the command and exit the output in a su.displayIO"""
    
    kwargs = {
        'args' : command,
        'cwd' : os.path.expanduser('~'),
        'stdout' : subprocess.PIPE,
        'stderr' : subprocess.PIPE,
        'universal_newlines' : True
    }
    
    output_txt = ''
    with subprocess.Popen(**kwargs) as p:
        for line in p.stdout:
            output_txt += line + '\n'
            if output:
                displayIO(output, line)
    
    return output_txt