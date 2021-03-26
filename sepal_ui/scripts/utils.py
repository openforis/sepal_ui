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
import os

import ipyvuetify as v
import pandas as pd
import ee
from cryptography.fernet import Fernet

import sepal_ui

def hide_component(widget):
    """
    hide a vuetify based component
    
    Args:
        widget (v.VuetifyWidget): the widget to hide
    """
    
    if isinstance(widget, sepal_ui.sepalwidgets.sepalwidget.SepalWidget):
        widget.hide()
    elif not 'd-none' in str(widget.class_):
        widget.class_ = str(widget.class_).strip() + ' d-none'
        
    return

def show_component(widget):
    """
    show a vuetify based component
    
    Args:
        widget (v.VuetifyWidget): the widget to hide
    """
    
    if isinstance(widget, sepal_ui.sepalwidgets.sepalwidget.SepalWidget):
        widget.show()
    elif 'd-none' in str(widget.class_):
        widget.class_ = widget.class_.replace('d-none', '')
        
    return 

def get_gaul_dic():
    """
    Create the list of the country code in the FAO GAUL norm using the CSV file provided in utils
        
    Return:
        (dict): the countries FAO_GAUL codes labelled with english country names
    """
    
    # file path
    path = Path(__file__).parent.joinpath('country_code.csv')
    
    # get the df and sort by country name
    df = pd.read_csv(path).sort_values(by=['ADM0_NAME'])
    
    # create the dict
    fao_gaul = {row['ADM0_NAME'] : row['ADM0_CODE'] for i, row in df.iterrows()}
        
    return fao_gaul

def get_iso_3(adm0):
    """
    Get the iso_3 code of a country_selection. Uses the fips_code if the iso-3 is not available
    
    Args:
        adm0 (int): the country adm0 code FAO GAUL 2015
        
    Return:
        (str): the 3 letters of the iso_3 country code
    """
    
    # file path
    path = Path(__file__).parent.joinpath('country_code.csv')
    
    # get the df
    df = pd.read_csv(path)
    
    row = df[df['ADM0_CODE'] == adm0]
    code = None
    if len(row):
        code = row['ISO 3166-1 alpha-3'].values[0]
        
    return code
    
def create_download_link(pathname):
    """
    Create a clickable link to download the pathname target
    
    Args:
        pathname (str | pathlib.Path): the pathname th download
        
    Return:
        (str): the download link
    """
    
    if type(pathname) == str:
        pathname = Path(pathname)
        
    result_path = Path(pathname).expanduser()
    home_path = Path('~').expanduser()
    
    # will be available with python 3.9
    #download_path = result_path.relative_to(home_path) if result_path.is_relative_to(home_path) else result_path
    download_path = os.path.relpath(result_path,home_path)
    
    link = f'/api/files/download?path=/{download_path}'
    
    return link

def is_absolute(url):
    """
    Check if the given url is an absolute or relative path
    
    Args:
        url (str): the url to test
        
    Return:
        (bool): True if absolute else False
    """
    return bool(urlparse(url).netloc)

def random_string(string_length=3):
    """
    Generates a random string of fixed length. 
    
    Args:
        string_length (int, optional): Fixed length. Defaults to 3.
    
    Return:
        (str): A random string
    """
    
    # random.seed(1001)
    letters = string.ascii_lowercase
    
    return ''.join(random.choice(letters) for i in range(string_length))

def get_file_size(filename):
    """
    Get the file size as string of 2 digit in the adapted scale (B, KB, MB....)
    
    Args:
        filename (str | pathlib.Path): the path to the file to mesure
        
    Return:
        (str): the file size in a readable humanly readable
    """
    
    file_size = Path(filename).stat().st_size
    
    if file_size == 0:
        return "0B"
    
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    
    i = int(math.floor(math.log(file_size, 1024)))
    s = file_size / (1024 ** i)
        
    return '{:.1f} {}'.format(s, size_name[i])

def init_ee():
    """
    Initialize earth engine according to the environment. 
    It will use the creddential file if the EE_PRIVATE_KEY env variable exist. 
    Otherwise it use the simple Initilize command (asking the user to register if necessary)
    """
    
    # only do the initialization if the credential are missing
    if not ee.data._credentials:
        
        # if the decrypt key is available use the decript key 
        if 'EE_DECRYPT_KEY' in os.environ:
        
            # read the key as byte 
            key = os.environ['EE_DECRYPT_KEY'].encode()
            
            # create the fernet object 
            fernet = Fernet(key)
            
            # decrypt the key
            json_encrypted = Path(__file__).parent.joinpath('encrypted_key.json')
            with json_encrypted.open('rb') as f:
                json_decripted = fernet.decrypt(f.read()).decode()
                
            # write it to a file
            with open('ee_private_key.json', 'w') as f:
                f.write(json_decripted)
                
            # connection to the service account
            service_account = 'test-sepal-ui@sepal-ui.iam.gserviceaccount.com'
            credentials = ee.ServiceAccountCredentials(service_account, 'ee_private_key.json')
            ee.Initialize(credentials)
        
        # if in local env use the local user credential
        else:
            ee.Initialize()
            
    return