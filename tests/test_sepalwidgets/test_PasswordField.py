import pytest

from sepal_ui import sepalwidgets as sw


class TestPasswordField:
    def test_init(self, password):

        assert isinstance(password, sw.PasswordField)
        assert password.type == "password"

        return

    def test_toogle_viz(self, password):

        # change the viz once
        password._toggle_pwd(None, None, None)
        assert password.type == "text"
        assert password.append_icon == "fa-solid fa-eye"

        # change it a second time
        password._toggle_pwd(None, None, None)
        assert password.type == "password"
        assert password.append_icon == "fa-solid fa-eye-slash"

        return

    @pytest.fixture
    def password(self):
        """return a passwordfield."""
        return sw.PasswordField()
