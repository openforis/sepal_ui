import unittest

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestStateBar(unittest.TestCase):
    def test_init(self):

        # minimal tooltip on a btn
        btn = sw.Btn("click")
        tooltip = sw.Tooltip(widget=btn, tooltip="Click over the button")

        # assert that a slot cannot be modified
        with self.assertRaises(Exception):
            tooltip.bottom = False

        return
