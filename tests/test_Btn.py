import unittest

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestBtn(unittest.TestCase):
    def test_init(self):

        # minimal btn
        btn = sw.Btn()
        self.assertEqual(btn.color, "primary")
        self.assertEqual(btn.v_icon, None)
        self.assertEqual(btn.children[0], "Click")

        # extensive btn
        btn = sw.Btn("toto", "mdi-folder")
        self.assertEqual(btn.children[1], "toto")
        self.assertIsInstance(btn.v_icon, v.Icon)
        self.assertEqual(btn.v_icon.children[0], "mdi-folder")

        return

    def test_set_icon(self):

        # new icon
        icon = "mdi-folder"
        btn = sw.Btn().set_icon(icon)

        self.assertIsInstance(btn.v_icon, v.Icon)
        self.assertEqual(btn.v_icon.children[0], icon)

        # change existing icon
        icon = "mdi-file"
        btn.set_icon(icon)
        self.assertEqual(btn.v_icon.children[0], icon)

        return

    def test_toggle_loading(self):

        btn = sw.Btn().toggle_loading()

        self.assertTrue(btn.loading)
        self.assertTrue(btn.disabled)

        btn.toggle_loading()
        self.assertFalse(btn.loading)
        self.assertFalse(btn.disabled)

        return


if __name__ == "__main__":
    unittest.main()
