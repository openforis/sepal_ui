import pytest
from unittest.mock import patch

import random
import os
from pathlib import Path

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su


class TestUtils:
    def test_hide_component(self):

        # hide a normal v component
        widget = v.Btn()
        su.hide_component(widget)
        assert "d-none" in widget.class_

        # hide a sepalwidget
        widget = sw.Btn()
        su.hide_component(widget)
        assert widget.viz == False

        return

    def test_show_component(self):

        # show a normal v component
        widget = v.Btn()
        su.hide_component(widget)
        su.show_component(widget)
        assert not "d-none" in widget.class_

        # show a sepalwidget
        widget = sw.Btn()
        su.hide_component(widget)
        su.show_component(widget)
        assert widget.viz == True

        return

    def test_download_link(self):

        # check the URL for a 'toto/tutu.png' path
        path = "toto/tutu.png"

        expected_link = "/api/files/download?path="

        res = su.create_download_link(path)

        assert expected_link in res

        return

    def test_is_absolute(self):

        # test an absolute URL (wikipedia home page)
        link = "https://fr.wikipedia.org/wiki/Wikipédia:Accueil_principal"
        su.is_absolute(link) == True

        # test a relative URL ('toto/tutu.html')
        link = "toto/tutu.html"
        assert su.is_absolute(link) == False

        return

    def test_random_string(self):

        # use a seed for the random function
        random.seed(1)

        # check default length
        str_ = su.random_string()
        assert len(str_) == 3
        assert str_ == "esz"

        # check parameter length
        str_ = su.random_string(6)
        assert len(str_) == 6
        assert str_ == "ycidpy"

        return

    def test_get_file_size(self):

        # init test values
        test_value = 7.5
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

        # mock 0 B file
        with patch("pathlib.Path.stat") as stat:
            stat.return_value.st_size = 0

            txt = su.get_file_size("random")
            assert txt == "0B"

        # mock every pow of 1024 to YB
        for i in range(9):
            with patch("pathlib.Path.stat") as stat:
                stat.return_value.st_size = test_value * (1024 ** i)

                txt = su.get_file_size("random")
                assert txt == f"7.5 {size_name[i]}"

        return

    def test_init_ee(self):

        # check that no error is raised
        res = su.init_ee()

        return

    def test_catch_errors(self):

        # create a fake object that uses the decorator
        class Obj:
            def __init__(self):
                self.alert = sw.Alert()
                self.btn = sw.Btn()

                self.func = su.catch_errors(alert=self.alert)(self.func)
                self.btn.on_event("click", self.func)

            def func(self, *args):
                return 1 / 0

        obj = Obj()
        obj.btn.fire_event("click", None)

        assert obj.alert.type == "error"

        return

    def test_loading_button(self):

        # create a fake object that uses the decorator
        class Obj:
            def __init__(self):
                self.alert = sw.Alert()
                self.btn = sw.Btn()
                self.func = su.loading_button(
                    alert=self.alert, button=self.btn, debug=False
                )(self.func)

                self.btn.on_event("click", self.func)

            def func(sel, *args):
                return 1 / 0

        obj = Obj()
        obj.btn.fire_event("click", None)

        assert obj.btn.disabled == False
        assert obj.alert.type == "error"

        # create a fake object that uses the decorator
        class Obj:
            def __init__(self):
                self.alert = sw.Alert()
                self.btn = sw.Btn()

                self.btn.on_event("click", self.func)

            @su.loading_button(debug=True)
            def func(self, *args):
                return 1 / 0

        obj = Obj()
        obj.btn.fire_event("click", None)

        assert obj.btn.disabled == False
        assert obj.alert.type == "error"

        return

    def test_to_colors(self):

        # setup the same color in several formats
        colors = {
            "hex": "#b8860b",
            "rgb": (0.7215686274509804, 0.5254901960784314, 0.043137254901960784),
            "rgb_int": (184, 134, 11),
            "gee_hex": "b8860b",
            "text": "darkgoldenrod",
        }

        for c in colors.values():
            res = su.to_colors(c)
            assert res == colors["hex"]

        # test that a fake one return black
        res = su.to_colors("toto")
        assert res == "#000000"

        return

    def test_switch(self, capsys):

        # create a fake object that uses the decorator
        class Obj:
            def __init__(self):
                self.valid = True
                self.select = v.Select(disabled=False)
                self.select2 = v.Select(disabled=False)

                # apply on non string
                self.func4 = su.switch("disabled", on_widgets=[self.select])(self.func4)

            # apply the widget on the object itself
            @su.switch("valid")
            def func1(self, *args):
                return True

            # apply the widget on members of the object
            @su.switch("disabled", on_widgets=["select", "select2"])
            def func2(self, *args):
                return True

            # apply it on a non existent widget
            @su.switch("niet", on_widgets=["fake_widget"])
            def func3(self, *args):
                return True

            def func4(self, *args):
                return True

            # apply on a error func with debug = True
            @su.switch("valid", debug=True)
            def func5(self, *args):
                return 1 / 0

        obj = Obj()

        # assert
        obj.func1()
        assert obj.valid == True

        obj.func2()
        assert obj.select.disabled == False
        assert obj.select2.disabled == False

        with pytest.raises(Exception):
            obj.func3()

        with pytest.raises(Exception):
            obj.func4()

        with pytest.raises(Exception):
            obj.func5()

        return
