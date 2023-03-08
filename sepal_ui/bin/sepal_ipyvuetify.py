#!/usr/bin/python3

"""Script to create an automatic overwrite of all the object in ipyvuetify.

We want to add SepalWidgets to the list of parent class.
This script should be run only by maintainer when changes are made to ipyvuetify itself. Please report to the issue tracker if any class is not available.
"""

import argparse
from datetime import datetime
from pathlib import Path

import ipyvuetify as v

parser = argparse.ArgumentParser(description=__doc__, usage="sepal_ipyvuetify")


def disclaimer() -> str:
    """Return the module docstring."""
    return (
        '"""All the ipyvuetify class override as SepalWidgets\n'
        "\n"
        "This file overwrite all the widgets generating by ipyvuetify to add the SepalWidget class as a parent.\n"
        "It should not be modified from here as it's automatically generated.\n"
        "\n"
        f"last update: {datetime.now():%Y-%m-%d}\n"
        '"""\n'
        "\n"
    )


def imports() -> str:
    """Return the import statements."""
    return (
        "import ipyvuetify as v\n"
        "from sepal_ui.sepalwidgets.sepalwidget import SepalWidget\n"
        "\n"
    )


def klass(klass: str) -> str:
    """Return the class line."""
    return f"class {klass}(v.{klass}, SepalWidget):\n" "    pass\n" "\n"


def is_widget(klass: str) -> bool:
    """Return True i the class is a widget."""
    not_hidden = not klass.startswith("__")
    not_main = klass != "VuetifyWidget"

    return not_hidden and not_main


def main() -> None:
    """Launch the process."""
    # parse agruments
    parser.parse_args()

    # name of the created file
    filename = Path(__file__).parents[1] / "sepalwidgets" / "sepal_ipyvuetify.py"

    # write the content of the file
    with filename.open("w") as f:
        f.write(disclaimer())
        f.write(imports())
        f.write(klass("Html"))  # not included in the c_list

        c_list = [c for c in dir(v.generated) if is_widget(c)]
        for c in c_list:
            f.write(klass(c))

    return


if __name__ == "__main__":
    main()
