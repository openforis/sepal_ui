from datetime import datetime

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestMarkdown:
    def test_init(self):

        ###################################################
        ##      TODO don't know how to test the txt      ##
        ###################################################

        # default init
        mkd_widget = sw.Markdown()
        assert isinstance(mkd_widget, v.Layout)
        assert isinstance(mkd_widget.children[0], v.Flex)
        # self.assertEqual(mkd_widget.children[0], '<div>\n\n</div>')

        # exhaustive
        txt = "toto"
        mkd_widget = sw.Markdown(txt)
        # self.assertEqual(mkd_widget.children[0], '<div>\n{}\n</div>'.format(txt))

        return
