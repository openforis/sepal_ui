"""Test the Footer widget"""

from datetime import datetime

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


def test_init() -> None:
    """init the widget"""
    # default init
    footer = sw.Footer()

    assert isinstance(footer, v.Footer)
    assert footer.children[0] == f"SEPAL \u00A9 {datetime.today().year}"

    # exhaustive
    title = "toto"
    footer = sw.Footer(title)
    assert footer.children[0] == title

    return
