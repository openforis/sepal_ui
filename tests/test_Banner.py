from sepal_ui import color
import sepal_ui.sepalwidgets as sw
import pytest


class TestBanner:
    def test_fail_type(self):
        """When using non-allowed types"""

        with pytest.raises(ValueError):
            sw.Banner(
                msg="message",
                type_="wrong_type",
            )

    def test_init(self):
        """Test basic initialization"""

        # Arrange
        msg = "dummy message"
        type_ = "warning"
        id_ = "test_banner"

        # Act
        banner = sw.Banner(msg=msg, type_=type_, id_=id_, timeout=True)

        # Assert
        assert banner.v_model is True
        assert banner.children[0] == msg
        assert banner.color == getattr(color, type_)
        assert banner.attributes["id"] == id_

    def test_close(self, banner):
        """Test close button"""

        banner.children[1].fire_event("click", None)

        assert banner.v_model is False

    def test_timeout(self, banner):
        """Test timeout result based on known text"""

        timeout = banner.get_timeout(banner.children[0])

        assert timeout == 3366.666666666667
        assert banner.v_model is True

    def test_no_timeout(self):
        """Test timeout value when not set"""

        banner = sw.Banner(msg="message", timeout=False)

        assert banner.timeout == 0

    @pytest.fixture
    def banner(self):
        """Return a default dummy Banner"""

        msg = "dummy message"
        type_ = "warning"
        id_ = "test_banner"

        return sw.Banner(msg=msg, type_=type_, id_=id_, timeout=True)
