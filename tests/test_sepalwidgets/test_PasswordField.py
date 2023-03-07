"""Test the Password widget"""


from sepal_ui import sepalwidgets as sw


def test_init() -> None:
    """Init the widget"""

    password = sw.PasswordField()
    assert isinstance(password, sw.PasswordField)
    assert password.type == "password"

    return


def test_toogle_viz() -> None:
    """Check tvisz roggle of the widget"""

    password = sw.PasswordField()

    # change the viz once
    password._toggle_pwd(None, None, None)
    assert password.type == "text"
    assert password.append_icon == "fa-solid fa-eye"

    # change it a second time
    password._toggle_pwd(None, None, None)
    assert password.type == "password"
    assert password.append_icon == "fa-solid fa-eye-slash"

    return
