"""The legacy SepalClient verbs are gone in pysepal 4.0."""

import pytest
from pysepal_api import SepalClient as ApiSepalClient

from pysepal.solara import session_manager as sm


def test_the_shim_module_is_gone():
    with pytest.raises(ModuleNotFoundError):
        __import__("pysepal.scripts.sepal_client")


def test_session_manager_uses_the_api_client_directly():
    assert sm.SepalClient is ApiSepalClient


@pytest.mark.parametrize("verb", ["get_remote_dir", "set_file", "list_files", "get_file"])
def test_legacy_verbs_are_not_on_the_api_client(verb):
    assert not hasattr(ApiSepalClient, verb)
