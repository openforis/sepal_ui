#!/usr/bin/python3

"""
Script to create a GEE credential file from a environment variable.

The script should be run in CD/CI environment as Github actions. It copy the credentials saved by maintainers in the "EARTHENGINE_TOKEN" environment variable and copy them to the appropriate file so that the test can be run. Note that the credentials have expiration dates so it will need to be changed on regular basis. Not intended for local dev as the user should be authenticated.
"""

import argparse
import os
from pathlib import Path

from colorama import Fore, init

# init colors for all plateforms
init()

# init parser
parser = argparse.ArgumentParser(description=__doc__, usage="ee_token")


def set_credentials(ee_token: str) -> None:
    """
    Set the credentials of the earthengine account based on ee_token.

    Args:
        ee_token: the str representation of existing GEE credentials
    """

    # write them in the appropriate file
    credential_folder_path = Path.home() / ".config" / "earthengine"
    credential_folder_path.mkdir(parents=True, exist_ok=True)
    credential_file_path = credential_folder_path / "credentials"
    with credential_file_path.open("w") as f:
        f.write(ee_token)

    return


def main() -> None:

    # read arguments (there should be none)
    parser.parse_args()

    # welcome the user
    print("Creating credentials for your build environment\n\n")

    # check if the environment variable is available
    ee_token = os.environ["EARTHENGINE_TOKEN"]

    # create the file
    set_credentials(ee_token)

    # display one last message
    print(f"{Fore.GREEN}The GEE credentials have been set.{Fore.RESET}")

    return


if __name__ == "__main__":
    main()
