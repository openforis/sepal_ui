"""Tests for the PYSEPAL_DEV_AUTH local-development login."""

from types import SimpleNamespace

import pytest

from pysepal.solara import dev_auth
from pysepal.solara._topology import DEV_AUTH_ENV_VAR


def _headers(username="alice"):
    return SimpleNamespace(
        sepal_user=SimpleNamespace(username=username),
        cookies={"SEPAL-SESSIONID": "sid-1"},
    )


def test_dev_auth_logs_in_once_per_process(monkeypatch):
    """get_sepal_headers_from_auth is a blocking POST; it must not repeat."""
    monkeypatch.setenv(DEV_AUTH_ENV_VAR, "1")
    logins = []
    parsed = _headers()

    def _login():
        logins.append(1)
        return parsed

    monkeypatch.setattr(dev_auth, "get_sepal_headers_from_auth", _login)

    assert dev_auth.prime_dev_auth() is parsed
    assert dev_auth.prime_dev_auth() is parsed
    assert logins == [1]


def test_dev_auth_refuses_to_log_in_when_it_is_not_armed(monkeypatch):
    """A developer login must be impossible to reach by accident."""
    monkeypatch.delenv(DEV_AUTH_ENV_VAR, raising=False)
    monkeypatch.setattr(
        dev_auth,
        "get_sepal_headers_from_auth",
        lambda: pytest.fail("must not log in when PYSEPAL_DEV_AUTH is unset"),
    )

    with pytest.raises(RuntimeError, match=DEV_AUTH_ENV_VAR):
        dev_auth.prime_dev_auth()


def test_resetting_the_cache_forces_a_new_login(monkeypatch):
    monkeypatch.setenv(DEV_AUTH_ENV_VAR, "1")
    logins = []
    monkeypatch.setattr(
        dev_auth, "get_sepal_headers_from_auth", lambda: logins.append(1) or _headers()
    )

    dev_auth.prime_dev_auth()
    dev_auth._reset_dev_auth_cache()
    dev_auth.prime_dev_auth()

    assert logins == [1, 1]


def test_solara_test_is_gone():
    """The old variable is deleted, not aliased.

    Its cached headers were shared across connections, so a multi-user
    container under SOLARA_TEST handed every user the same session.
    """
    import pysepal.solara.session_manager as session_manager

    assert not hasattr(session_manager, "_dev_auth_enabled")
    assert not hasattr(session_manager, "reset_dev_headers_cache")
    assert "reset_dev_headers_cache" not in session_manager.__all__
    assert "SOLARA_TEST" not in (session_manager.__doc__ or "")


def test_prime_dev_auth_is_public_api():
    import pysepal.solara as ps

    assert ps.prime_dev_auth is dev_auth.prime_dev_auth
    assert "prime_dev_auth" in ps.__all__
