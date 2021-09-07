from sepal_ui import sepalwidgets as sw


class TestPasswordField:
    def test_init(self):

        # default init
        password = sw.PasswordField()

        assert isinstance(password, sw.PasswordField)
        assert password.type == "password"

        return

    def test_toogle_viz(self):

        # default init
        password = sw.PasswordField()

        # change the viz once
        password._toggle_pwd(None, None, None)
        assert password.type == "text"
        assert password.append_icon == "mdi-eye"

        # change it a second time
        password._toggle_pwd(None, None, None)
        assert password.type == "password"
        assert password.append_icon == "mdi-eye-off"

        return
