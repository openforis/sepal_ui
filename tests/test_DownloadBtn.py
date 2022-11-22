import pytest
from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts.utils import create_download_link


class TestDownloadBtn:
    def test_init(self, file_start):

        # default init
        txt = "toto"
        btn = sw.DownloadBtn(txt)

        assert isinstance(btn, sw.DownloadBtn)
        assert btn.children[0].children[0] == "fas fa-download"
        assert btn.children[1] == txt
        assert file_start in btn.href
        assert "#" in btn.href
        assert btn.target == "_blank"
        assert btn.disabled is True
        assert btn.attributes["download"] is None

        # exhaustive
        link = "toto/ici"
        btn = sw.DownloadBtn(txt, link)
        assert link in btn.href
        assert btn.disabled is False
        assert btn.attributes["download"] is not None

        # absolute link
        absolute_link = "http://www.fao.org/home/en/"
        btn = sw.DownloadBtn(txt, absolute_link)
        assert absolute_link == btn.href

        return

    def test_set_url(self):

        # parameters
        link = "toto/ici"

        # default init
        txt = "toto"
        btn = sw.DownloadBtn(txt)

        # add a link
        res = btn.set_url(link)

        assert res == btn
        assert link in btn.href
        assert btn.disabled is False
        assert btn.attributes["download"] is not None

        # reset
        btn.set_url()
        assert "#" in btn.href
        assert btn.disabled is True
        assert btn.attributes["download"] is None

        return

    def test_create_download_link(self, file_start):

        # relative link
        relative_link = "toto/ici"

        path = create_download_link(relative_link)

        assert file_start in path
        assert relative_link in path

        return

    @pytest.fixture
    def file_start(self):
        """the start of any link to the sepal platform"""

        return "https://sepal.io/api/sandbox/jupyter/files/"
