"""Test the Markdown widget"""

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


def test_init() -> None:
    """Init the widget"""
    # default init
    mkd_widget = sw.Markdown()
    expected = "<div>\n\n</div>"
    assert isinstance(mkd_widget, v.Layout)
    assert isinstance(mkd_widget.children[0], v.Flex)
    assert mkd_widget.children[0].children[0].template == expected

    return


def test_init_exhaustive() -> None:
    """Init the widget"""
    # exhaustive
    txt = "toto"
    expected = f"<div>\n<p>{txt}</p>\n</div>"
    mkd_widget = sw.Markdown(txt)
    assert mkd_widget.children[0].children[0].template == expected

    return


def test_init_link() -> None:
    """Test links are set to be opened in a blank page"""
    # add a link
    link_name = "toto"
    link = "#"
    txt = f"[{link_name}]({link})"
    expected = f'<div>\n<p><a target="_blank" href="{link}">{link_name}</a></p>\n</div>'
    mkd_widget = sw.Markdown(txt)
    assert mkd_widget.children[0].children[0].template == expected

    return
