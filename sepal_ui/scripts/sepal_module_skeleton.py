#!/usr/bin/python3
import re 
import os 
from pathlib import Path
import subprocess

if __name__ == "__main__":
    
    # welcome the user 
    print("##################################")
    print("#                                #")
    print("#      SEPAL MODULE FACTORY      #")
    print("#                                #")
    print("##################################")
    print()
    print()
    print()
    print("Welcome in the module factory interface.")
    print("This interface will help you building a dashboard app based on the sepal_ui librairy")
    print("Please read the documentation of the librairy before launching this script")
    print()
    print()
    print()
    print("Initializing module creation by setting up your module parameters")
    
    # ask the name of the module 
    module_name = input('Please provide you module name: ')
    if not module_name:
        raise Exception("A module name should be set")
        
    # set the module github url 
    github_url = input('Provide the url of the empty github repository: ')
    if not module_name:
        raise Exception("A module name should be set with an asociated github repository")
        
    # ask for a short description 
    description = input('Provide a short description for your module (it can be the same as the one you provided on github): ')
    
    # adapt the name of the module to remove any special characters and spaces
    normalized_name = re.sub('[^a-zA-Z\d\-\_]', '_', module_name)
    
    # clone the repository in a folder that has the normalized module name 
    folder = Path('~', normalized_name).expanduser()
    template_url = "https://github.com/12rambau/sepal_ui_template.git"
    
    command = ['git', 'clone', template_url, str(folder)]
    res = subprocess.run(command, cwd=Path.home())
    
    # remove the .git folder 
    command = ["rm", "-rf", str(folder.joinpath('.git'))]
    res = subprocess.run(command, cwd=Path.home())
    
    # replace the placeholders 
    
    
    # init the new git repository
    command = ['git', 'init']
    res = subprocess.run(command, cwd=folder)
    
    # add all the files in the git repo
    command = ['git', 'add', '.']
    res = subprocess.run(command, cwd=folder)
    
    # first commit 
    command = ['git', 'commit', '-m', "first commit"]
    res = subprocess.run(command, cwd=folder)
    
    # create a branch   
    command = ['git', 'branch', '-M', 'master']
    res = subprocess.run(command, cwd=folder)
    
    # add the remote 
    command = ['git', 'remote', 'add', 'origin', github_url]
    res = subprocess.run(command, cwd=folder)
    
    # make the first push 
    command = ['git', 'push', '-u', 'origin', 'master']
    res = subprocess.run(command, cwd=folder)
    
    # exit message
    print("Congratulation you created a new module")
    print("Let's code !")
    
    