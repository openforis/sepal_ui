import time
from datetime import datetime
import os
import glob
from pathlib import Path
import csv
from urllib.parse import urlparse
import subprocess
import string 
import random
import math
import base64

import ipyvuetify as v
import pandas as pd
import ee

import sepal_ui

def hide_component(widget):
    """hide a vuetify based component"""
    
    if isinstance(widget, sepal_ui.sepalwidgets.sepalwidget.SepalWidget):
        widget.hide()
    elif not 'd-none' in str(widget.class_):
        widget.class_ = str(widget.class_).strip() + ' d-none'
        
    return

def show_component(widget):
    """show a vuetify based component"""
    if isinstance(widget, sepal_ui.sepalwidgets.sepalwidget.SepalWidget):
        widget.show()
    elif 'd-none' in str(widget.class_):
        widget.class_ = widget.class_.replace('d-none', '')
        
    return 

def get_gaul_dic():
    """create the list of the country code in the FAO GAUL norm using the CSV file provided in utils
        
    Returns:
        fao_gaul (dic): the countries FAO_GAUL codes labelled with english country names
    """
    
    # file path
    path = os.path.join(os.path.dirname(__file__), 'country_code.csv')
    
    # get the df and sort by country name
    df = pd.read_csv(path).sort_values(by=['country_na'])
    
    # create the dict
    fao_gaul = {row['country_na'] : row['GAUL'] for i, row in df.iterrows()}
        
    return fao_gaul

def get_iso_3(country_name):
    """return the iso_3 code of a country_selection. Uses the fips_code if the iso-3 is not available"""
    
    #file path
    path = os.path.join(os.path.dirname(__file__), 'country_code.csv')
    
    # get the df
    df = pd.read_csv(path)
    
    row = df[df['country_na'] == country_name]
    
    if len(row):
        code = row['ISO 3166-1 alpha-3'].values[0]
        
    return code
    
def create_download_link(pathname):
    """return a clickable link to download the pathname target"""
    
    result_path = os.path.expanduser(pathname)
    home_path = os.path.expanduser('~')
    download_path='/'+os.path.relpath(result_path,home_path)
    
    link = f'/api/files/download?path={download_path}'
    
    return link

def is_absolute(url):
    """ check if the given url is an absolute or relative path"""
    return bool(urlparse(url).netloc)

def random_string(string_length=3):
    """Generates a random string of fixed length. 
    Args:
        string_length (int, optional): Fixed length. Defaults to 3.
    Returns:
        str: A random string
    """
    # random.seed(1001)
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))

def get_file_size(filename):
    """return the file size as string of 2 digit in the adapted scale (B, KB, MB....)"""
    
    #file_size = Path(filename).stat().st_size
    file_size = os.path.getsize(filename)
    
    if file_size == 0:
        return "0B"
    
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    
    i = int(math.floor(math.log(file_size, 1024)))
    s = file_size / (1024 ** i)
        
    return '{:.1f} {}'.format(s, size_name[i])

def init_ee():
    """Initialize earth engine according to the environment"""
    
    # only do the initialization if the credential are missing
    if not ee.data._credentials:
        
        # if in test env use the private key
        if 'EE_PRIVATE_KEY' in os.environ:
            
            # key need to be decoded in a file
            content = base64.b64decode(os.environ['EE_PRIVATE_KEY']).decode()
            with open('ee_private_key.json', 'w') as f:
                f.write(content)
    
            # connection to the service account
            service_account = 'test-sepal-ui@sepal-ui.iam.gserviceaccount.com'
            credentials = ee.ServiceAccountCredentials(service_account, 'ee_private_key.json')
            ee.Initialize(credentials)
        
        # if in local env use the local user credential
        else:
            ee.Initialize()
            
    return 0