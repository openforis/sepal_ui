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
