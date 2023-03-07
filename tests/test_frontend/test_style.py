from sepal_ui.frontend import styles as ss


def test_folders() -> None:
    """Assert folders are existing with the frontend files"""
    assert ss.JSON_DIR.is_dir()
    assert ss.CSS_DIR.is_dir()
    assert ss.JS_DIR.is_dir()

    return


def test_colors() -> None:
    """Assert the colors are customized as expected"""
    # test that colors have the same size and names
    assert len(ss.DARK_THEME.keys()) == len(ss.LIGHT_THEME.keys())
    assert all(dc in ss.LIGHT_THEME.keys() for dc in ss.DARK_THEME.keys())

    return
