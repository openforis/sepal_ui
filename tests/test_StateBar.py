import unittest

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestStateBar(unittest.TestCase):
    def test_init(self):

        # minimal state bar
        state_bar = sw.StateBar()
        self.assertEqual(len(state_bar.children), 2)

        return

    def test_add_msg(self):

        state_bar = sw.StateBar()

        # assert that add msg can add a msg without blocking the loading
        msg = "not finished"
        state_bar.add_msg(msg, True)

        self.assertEqual(state_bar.children[0].indeterminate, True)
        self.assertEqual(state_bar.msg, msg)

        # assert that add message can stop the loading
        msg = "finished"
        state_bar.add_msg(msg)

        self.assertEqual(state_bar.children[0].indeterminate, False)

        return
