import pytest

import sepal_ui.sepalwidgets as sw


class TestBanner:
    def test_init(self):
        """Test basic initialization"""

        # check a default one
        banner = sw.Banner()

        assert banner.v_model is True
        assert banner.children[0] == ""
        assert banner.color == "info"
        assert banner.attributes["id"] == ""
        assert banner.timeout == 0

        # exaustive definition
        msg = "toto"
        type_ = "warning"
        id_ = "test_banner"
        banner = sw.Banner(msg=msg, type_=type_, id_=id_, persistent=False)

        assert banner.children[0] == msg
        assert banner.color == type_
        assert banner.attributes["id"] == id_
        assert banner.timeout > 0

        # check the fallback to info
        banner = sw.Banner(type_="toto")

        assert banner.color == "info"

        return

    def test_close(self, banner):
        """Test close button"""

        banner.children[1].fire_event("click", None)

        assert banner.v_model is False

        return

    def test_get_timeout(self, banner):
        """Test timeout result based on known text"""

        timeout = banner.get_timeout(banner.children[0])

        assert timeout == 3366
        assert banner.v_model is True

        return

    @pytest.fixture
    def banner(self):
        """Return a default dummy Banner"""

        return sw.Banner(
            msg="dummy message", type_="warning", id_="test_banner", persistent=False
        )
