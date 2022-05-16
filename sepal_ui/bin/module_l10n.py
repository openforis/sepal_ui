#!/usr/bin/python3

"""
Script to manually change the used theme

This script will update the parameters shared between all sepal-ui based modules.
The "language" parameter will be changed to the selected one. Any running application will need to be restarted to use this modification
"""

import pandas as pd
from colorama import init, Fore
from pathlib import Path
import argparse

from sepal_ui.scripts import utils as su

# init colors for all plateforms
init()

# init the parser
parser = argparse.ArgumentParser(description=__doc__, usage="module_l10n")


def check_locale(locale):
    """
    Check if the locale exist in the country list

    Return:
        (bool)
    """

    countries = pd.read_csv(Path(__file__).parents[1] / "scripts" / "locale.csv")

    return locale in countries.code.values


def main():

    # parse agruments
    parser.parse_args()

    # welcome the user
    print(f"{Fore.YELLOW}sepal-ui localisation script{Fore.RESET}")

    # select a language
    is_locale = False
    while is_locale is False:

        locale = input(f"{Fore.CYAN}Provide a locale code: \n{Fore.RESET}")
        is_locale = check_locale(locale)

        # display an error if the language does not exist
        if is_locale is False:
            print(
                f'{Fore.RED} The provided language code ("{locale}") is not a valid language code in IETF BCP 47.{Fore.RESET}'
            )

    # write the new color code in the config file
    su.set_config_locale(locale)

    # display information
    print(
        f'{Fore.GREEN} The provided language code ("{locale}") has been set as default language for all SEPAL applications.{Fore.RESET}'
    )


if __name__ == "__main__":
    main()