import ipyvuetify as v

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts.utils import create_download_link


class TestDownloadBtn:
    def test_init(self):

        # default init
        txt = "toto"
        btn = sw.DownloadBtn(txt)
        start = "/api/files/download?path="

        assert isinstance(btn, sw.DownloadBtn)
        assert btn.children[0].children[0] == "mdi-download"
        assert btn.children[1] == txt
        assert start in btn.href
        assert "#" in btn.href
        assert btn.disabled == True

        # exhaustive
        link = "toto/ici"
        btn = sw.DownloadBtn(txt, link)
        assert link in btn.href
        assert btn.disabled == False

        # absolute link
        absolute_link = "http://www.fao.org/home/en/"
        btn = sw.DownloadBtn(txt, absolute_link)
        assert absolute_link == btn.href

        return

    def test_set_url(self):

        # parameters
        start = "/api/files/download?path="
        link = "toto/ici"

        # default init
        txt = "toto"
        btn = sw.DownloadBtn(txt)

        # add a link
        res = btn.set_url(link)

        assert res == btn
        assert link in btn.href
        assert btn.disabled == False

        # reset
        btn.set_url()
        assert "#" in btn.href
        assert btn.disabled == True

        return

    def test_create_download_link(self):

        # relative link
        start = "/api/files/download?path="
        relative_link = "toto/ici"

        path = create_download_link(relative_link)

        assert start in path
        assert relative_link in path

        return
