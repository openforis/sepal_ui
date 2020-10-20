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

import ipyvuetify as v
    
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