#!/usr/bin/python3

"""Script to create the skeleton of a sepal-ui module.

The script will extract the skeleton of a module from the sepal_ui_template GitHub repository. This template will be adapted based on the answsers to the questionnaire.
Placeholdre from the template will be replaced and the directory will be synced with a GitHub freshly created repository. Note that the repository need to be fully empty when the command is launched.
"""

import argparse
import json
import re
import subprocess
from distutils.util import strtobool
from pathlib import Path

from colorama import Fore, init

# init colors for all plateforms
init()

# init parser
parser = argparse.ArgumentParser(description=__doc__, usage="module_factory")


def set_default_readme(
    folder: Path, module_name: str, description: str, url: str
) -> None:
    """Write a default README.md file and overwrite the existing one.

    Args:
        folder: the module directory
        module_name: the module name used as title everywhere
        description: the description of the module
        url: the url of the module repository in GitHub
    """
    print("Write a default README.md file")

    license = f"{url}/blob/master/LICENSE"

    file = folder / "README.md"
    # write_text cannot handle append
    with file.open("w") as readme:
        readme.writelines(
            [
                f"# {module_name}\n",
                "\n",
                f"[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]({license})\n",
                "[![Black badge](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n",
                "\n",
                "# About\n",
                "\n",
                f"{description}\n",
            ]
        )

    return


def set_default_about(folder: Path, description: str) -> None:
    """Write a default ABOUT_en.md file and overwrite the existing one.

    Args:
        folder: the directory of the module
        description: the description of the module functions
    """
    print("Write a default ABOUT_en.md file")

    # creating the dir
    dir_ = folder / "utils"
    dir_.mkdir(exist_ok=True)

    # set the file
    file = dir_ / "ABOUT_en.md"

    with file.open("w") as about:
        about.write(f"{description}  \n")

    return


def set_module_name(folder: Path, module_name: str) -> None:
    """Use the module name in the different translation dictionaries.

    Args:
        folder: the directory of the module
        module_name: the module name
    """
    print("Update the module name in the json translation dictionaries")

    # edit the en file
    app_file = folder / "component" / "message" / "en" / "app.json"

    with app_file.open("r") as f:
        data = json.load(f)

    data["app"]["title"] = module_name

    with app_file.open("w") as f:
        json.dump(data, f, indent=4)

    return


def set_module_name_doc(folder: Path, url: str, module_name: str) -> None:
    """Set the module name in each documentation file and set the appropriate repository in the link.

    Args:
        folder: the directory of the module
        url: the url of the GitHub repository
        module_name: the module name
    """
    # get the documentation folder
    doc_dir = folder / "doc"

    # loop in the available languages
    for file in doc_dir.glob("*.rst"):

        with file.open() as f:
            text = f.read()

        text = text.replace("Module_name", module_name)
        text = text.replace("===========", "=" * len(module_name))
        text = text.replace("https://github.com/12rambau/sepal_ui", url)

        with file.open("w") as f:
            f.write(text)
    return


def set_drawer_link(folder: Path, url: str) -> None:
    """Replace the reference to the default repository to the one provided by the user.

    Args:
        folder: the directory of the module
        url: the url of the GitHub repository
    """
    print("Update the drawers link with the new repository one")

    # get the ui file
    ui = folder / "ui.ipynb"

    # read the file
    with ui.open() as f:
        ui_content = f.read()

    # replace the target strings
    ui_content = ui_content.replace("https://github.com/12rambau/sepal_ui", url)

    # write everything down again
    with ui.open("w") as f:
        f.write(ui_content)

    return


def main() -> None:
    """Launch the process."""
    # parse agruments
    parser.parse_args()

    # welcome the user
    print(f"{Fore.YELLOW}sepal-ui module factory{Fore.RESET}")

    print("Initializing module creation by setting up your module parameters")
    print("‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾")

    # ask the name of the module
    module_name = input(f"{Fore.CYAN}Provide a module name: \n{Fore.RESET}")
    if not module_name:
        raise Exception(f"{Fore.RED}A module name should be set")
    question = f"{Fore.CYAN}Provide the URL of an empty github repository: \n{Fore.RESET}"  # fmt: skip
    github_url = input(question)
    if not github_url:
        msg = f"{Fore.RED}A module name should be set with an asociated github repository"  # fmt: skip
        raise Exception(msg)
    question = f"{Fore.CYAN}Provide a short description for your module (optional): \n{Fore.RESET}"  # fmt: skip
    description = input(question)

    # default to a panel application
    question = f"{Fore.CYAN}Do you need a fullscreen application [n]? \n{Fore.RESET}"
    type_ = input(question)
    branch = "map_app" if bool(strtobool(type_)) is True else "panel_app"

    # adapt the name of the module to remove any special characters and spaces
    normalized_name = re.sub("[^a-zA-Z\d\-\_]", "_", module_name)

    print("Build the module init configuration")
    print("‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾")

    # clone the repository in a folder that has the normalized module name
    folder = Path.cwd() / normalized_name

    template_dir = Path(__file__).parents[1] / "templates" / branch / "."
    subprocess.run(["cp", "-r", str(template_dir), str(folder)], cwd=Path.cwd())

    # replace the placeholders
    url = github_url.replace(".git", "").replace(
        "git@github.com:", "https://github.com/"
    )

    set_default_readme(folder, module_name, description, url)
    set_default_about(folder, description)
    set_module_name(folder, module_name)
    set_drawer_link(folder, url)
    set_module_name_doc(folder, url, module_name)

    default = "main"

    # execute the creation process in command lines
    # - init the new git repository
    # - change default branch name if using an old version of git
    # - add the configuration of the git repository
    # - add all the files in the git repo
    # - run all the precommit at least once
    # - include the correction from pre-commits
    # - first commit
    # - create a branch
    # - add the remote
    # - make the first push
    # - create a release branch and push it to the server
    # - checkout to master
    subprocess.run(["git", "init"], cwd=folder)
    subprocess.run(["git", "checkout", "-b", default], cwd=folder)
    subprocess.run(["pre-commit", "install"], cwd=folder)
    subprocess.run(["git", "add", "."], cwd=folder)
    subprocess.run(["pre-commit", "run", "--all-files"], cwd=folder)
    subprocess.run(["git", "add", "."], cwd=folder)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=folder)
    subprocess.run(["git", "branch", "-M", default], cwd=folder)
    subprocess.run(["git", "remote", "add", "origin", str(github_url)], cwd=folder)
    subprocess.run(["git", "push", "-u", "origin", default], cwd=folder)
    subprocess.run(["git", "checkout", "-b", "release"], cwd=folder)
    subprocess.run(["git", "push", "--set-upstream", "origin", "release"], cwd=folder)
    subprocess.run(["git", "checkout", default], cwd=folder)

    # exit message
    print(
        f"{Fore.YELLOW}Have a look to the git command executed in the process. if any of them is displaying an error, the final folder may not have been created{Fore.RESET}"
    )
    print(
        f"{Fore.YELLOW}If that's the case, delete the folder in your sepal instance (if there is any) and start the process again or contact us via github issues.{Fore.RESET}"
    )
    print(f"{Fore.GREEN}You created a new module named: {module_name}{Fore.RESET}")
    print(
        f"{Fore.GREEN}You can find its code in {folder} inside your sepal environment.{Fore.RESET}"
    )
    print()
    print("Let's code !")


if __name__ == "__main__":
    main()
