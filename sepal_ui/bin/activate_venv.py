"""Script to manually activate one of the venv available in the current Jupyter environment.

Application are designed to run on specific venv, created to avoid lib deprecation.
this script allows the user to easily activate one of the venv have already installed in Jupyter and customize it
"""

import argparse
import subprocess
from pathlib import Path

import pandas as pd
from colorama import Fore, init

# init colors for all plateforms
init()

parser = argparse.ArgumentParser(description=__doc__, usage="activate_venv")


def main() -> None:
    """Activate the selected venv."""
    # parse agruments
    parser.parse_args()

    print(
        f"{Fore.CYAN} Welcome to the virtual env activation, loading your venvs... \n{Fore.RESET}"
    )

    # Get usr venvs
    result = subprocess.run(["jupyter", "kernelspec", "list"], stdout=subprocess.PIPE)

    venvs = pd.DataFrame(
        [
            line.split()
            for line in result.stdout.decode("utf-8").splitlines()
            if ".local" not in line
        ],
    ).iloc[1:]

    # Check if user has test envs
    test_venv_path = Path.home() / "module-venv"
    if test_venv_path.exists():
        test_envs = pd.DataFrame(
            list(
                [f"test {el.name}", str(el)]
                for el in test_venv_path.glob("[!.]*")
                if el.is_dir()
            )
        )
        venvs = pd.concat([venvs, test_envs])
    venvs = venvs.reset_index(drop=True)
    venvs.columns = ["env name", "path"]

    print(f"{Fore.CYAN} You can activate any of the following venvs: \n{Fore.RESET}")
    print(venvs)

    valid = False

    while not valid:

        selection = int(
            input(
                f"{Fore.CYAN} Select the venv number you want to activate: \n{Fore.RESET}"
            )
        )

        if selection not in venvs.index.unique():
            print(f"{Fore.RED}Your selection is not valid {Fore.RESET}")
        else:
            valid = True
    # Activate virtual env
    kernel_path = Path(venvs.iloc[selection]["path"])
    test = "module-venv" in str(kernel_path)

    activate_path = "bin/activate" if test else "venv/bin/activate"
    print(f"{Fore.GREEN}Activating: {kernel_path} {Fore.RESET}")

    # Based on https://stackoverflow.com/questions/6943208/activate-a-virtualenv-with-a-python-script
    # It won't return anything to know if the the command was succesfully done
    subprocess.run(
        ["/bin/bash", "--rcfile", str(kernel_path / activate_path)],
    )

    # The following lines won't be executed because the previous subprocess kill the kernel

    # Confirm that we are in the new env
    result = subprocess.run(
        ["echo", "$VIRTUAL_ENV"], shell=True, stdout=subprocess.PIPE
    )

    print(f"The current env is: {result.stdout!r}")

    return


if __name__ == "__main__":
    main()
