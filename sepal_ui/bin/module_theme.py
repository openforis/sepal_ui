#!/usr/bin/python3

"""Script to manually change the used theme.

This script will update the parameters shared between all sepal-ui based modules.
The "theme" parameter will be changed to the selected one. Any running application will need to be restarted to use this modification
"""

import argparse

from colorama import Fore, init

from sepal_ui.scripts import utils as su

# init colors for all plateforms
init()

# init parser
parser = argparse.ArgumentParser(description=__doc__, usage="module_theme")


def check_theme(theme: str) -> bool:
    """Check if the theme is a legit name.

    Args:
        theme: the theme name

    Returns:
        True if the theme is covered by sepal-ui
    """
    themes = ["dark", "light"]

    return theme in themes


def main() -> None:
    """Launch the process."""
    # parse agruments
    parser.parse_args()

    # welcome the user
    print(f"{Fore.YELLOW}sepal-ui module theme selection{Fore.RESET}")

    # select a language
    is_theme = False
    while is_theme is False:

        theme = input(f"{Fore.CYAN}Provide a theme name: \n{Fore.RESET}")
        is_theme = check_theme(theme)

        # display an error if the theme does not exist
        if is_theme is False:
            print(
                f'{Fore.RED} The provided theme name ("{theme}") is not a supported theme. {Fore.RESET}'
            )

    # write the new color code in the config file
    su.set_config_theme(theme)

    # display information
    print(
        f'{Fore.GREEN} The provided theme ("{theme}") has been set as default theme for all SEPAL applications.{Fore.RESET}'
    )

    return


if __name__ == "__main__":
    main()
