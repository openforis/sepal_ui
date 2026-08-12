"""One import path for the session error hierarchy."""

from pysepal.solara import errors, session_manager


def test_hierarchy():
    assert issubclass(errors.MissingSepalHeadersError, errors.SepalSessionError)
    assert issubclass(errors.SessionScopeClosedError, errors.SepalSessionError)
    assert issubclass(errors.SepalSessionError, RuntimeError)


def test_session_manager_does_not_re_export_them():
    """Two import paths for one name is a compat surface; there is one path."""
    for name in (
        "SepalSessionError",
        "MissingSepalHeadersError",
        "SessionScopeClosedError",
    ):
        assert name not in session_manager.__all__
