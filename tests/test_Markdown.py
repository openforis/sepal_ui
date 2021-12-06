import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestMarkdown:
    def test_init(self):

        # default init
        mkd_widget = sw.Markdown()
        expected = "<div>\n\n</div>"
        assert isinstance(mkd_widget, v.Layout)
        assert isinstance(mkd_widget.children[0], v.Flex)
        assert mkd_widget.children[0].children[0].template == expected

        return

    def test_init_exhaustive(self):

        # exhaustive
        txt = "toto"
        expected = f"<div>\n<p>{txt}</p>\n</div>"
        mkd_widget = sw.Markdown(txt)
        assert mkd_widget.children[0].children[0].template == expected

        return

    def test_init_link(self):

        # add a link
        link_name = "toto"
        link = "#"
        txt = f"[{link_name}]({link})"
        expected = (
            f'<div>\n<p><a target="_blank" href="{link}">{link_name}</a></p>\n</div>'
        )
        mkd_widget = sw.Markdown(txt)
        assert mkd_widget.children[0].children[0].template == expected

        return
