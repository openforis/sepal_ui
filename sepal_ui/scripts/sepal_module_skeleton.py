#!/usr/bin/python3
import re 
import os 
from pathlib import Path
import subprocess
import json

from colorama import init, Fore, Style

#init colors for all plateforms
init()

def set_default_readme(folder, module_name, description):
    """write a default README.md file and overwrite the existing one"""
    
    print('Write a default README.md file')
    
    with open(folder.joinpath('README.md'), "w") as readme:
        
        readme.write(f'# {module_name}  \n')
        readme.write('[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  \n')
        readme.write('  \n')
        readme.write('## About  \n')
        readme.write('  \n')
        readme.write(f'{description}  \n')
    
    return 

def set_default_about(folder, description):
    """write a default ABOUT.md file and overwrite the existing one"""
    
    print('Write a default ABOUT.md file')
    
    with open(folder.joinpath('utils', 'ABOUT.md'), "w") as about:
        
        about.write(f'{description}  \n')
        
    return

def set_module_name(folder, module_name):
    """use the module name in the different translation dictionaries"""
    
    print('Update the module name in the json translation dictionnaries')
    
    #loop in the available languages
    languages = ['en', 'fr']
    for lang in languages:
    
        file = folder.joinpath('component', 'message', f'{lang}.json')
        
        with open(file, "r") as f:
            data = json.load(f)

        data['app']['title'] = module_name

        with open(file, "w") as f:
            json.dump(data, f)
            
    return
    

if __name__ == "__main__":
    
    # welcome the user 
    print(Fore.YELLOW)
    print("##################################")
    print("#                                #")
    print("#      SEPAL MODULE FACTORY      #")
    print("#                                #")
    print("##################################")
    print(Fore.RESET)
    print(f"Welcome in the {Style.BRIGHT}module factory{Style.NORMAL} interface.")
    print("This interface will help you building a dashboard app based on the sepal_ui librairy")
    print("Please read the documentation of the librairy before launching this script")
    print()
    print()
    print()
    print("Initializing module creation by setting up your module parameters")
    print("‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾")
    print()
    
    # ask the name of the module 
    module_name = input(f'{Fore.CYAN}Provide a module name: \n{Fore.RESET}')
    if not module_name:
        raise Exception(f"{Fore.RED}A module name should be set")
        
    # set the module github url 
    github_url = input(f'{Fore.CYAN}Provide the url of an empty github repository: \n{Fore.RESET}')
    if not module_name:
        raise Exception(f"{Fore.RED}A module name should be set with an asociated github repository")
        
    # ask for a short description 
    description = input(f'{Fore.CYAN}Provide a short description for your module(optional): \n{Fore.RESET}')
    
    # adapt the name of the module to remove any special characters and spaces
    normalized_name = re.sub('[^a-zA-Z\d\-\_]', '_', module_name)
    
    print()
    print("Build the module init configuration")
    print("‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾")
    print()
    
    # clone the repository in a folder that has the normalized module name 
    folder = Path('~', normalized_name).expanduser()
    template_url = "https://github.com/12rambau/sepal_ui_template.git"
    command = ['git', 'clone', template_url, str(folder)]
    res = subprocess.run(command, cwd=Path.home())
    
    # remove the .git folder 
    command = ["rm", "-rf", str(folder.joinpath('.git'))]
    res = subprocess.run(command, cwd=Path.home())
    
    # replace the placeholders 
    set_default_readme(folder, module_name, description)
    set_default_about(folder, description)
    set_module_name(folder, module_name)
    
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
    print(Fore.YELLOW)
    print('WARNING: have a look to the git command executed in the process. if any of them is displaying an error, the final folder may not have been created')
    print("If thats the case, delete the folder in your sepal instance (if there is any) and start the process again or contact us via github issues")
    print(Fore.GREEN)
    print(f"CONGRATULATION: You created a new module named: {Style.BRIGHT}{module_name}{Style.NORMAL}")
    print(f"You can find its code in {Style.BRIGHT}{folder}{Style.NORMAL} inside your sepal environment.")
    print("To go further in the development of your application you can have a look at the sepalizing documentation.")
    print()
    print("Let's code !")
    print(Fore.RESET)
    
    