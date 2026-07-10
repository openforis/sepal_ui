"""Tests for the deprecated SepalClient compat shim (pysepal/scripts/sepal_client.py)."""
from pathlib import PurePosixPath
from unittest import mock

import pytest
from pysepal_api import SepalClient as ApiSepalClient
from pysepal_api.auth import NoAuth
from pysepal_api.models import DirectoryListing, FileEntry, FileWriteResult

from pysepal.scripts.sepal_client import SepalClient


@pytest.fixture
def shim():
    """A shim client with a stubbed `.files` (construction does no network I/O)."""
    client = SepalClient(base_url="https://sepal.test", auth=NoAuth())
    client.files = mock.MagicMock()
    yield client
    client.close()


def test_is_subclass_of_api_client_with_legacy_verbs():
    assert issubclass(SepalClient, ApiSepalClient)
    for verb in ("get_remote_dir", "set_file", "list_files", "get_file"):
        assert callable(getattr(SepalClient, verb))


def test_get_remote_dir_delegates_to_files_mkdir(shim):
    shim.files.mkdir.return_value = PurePosixPath("module_results/demo")
    with pytest.warns(DeprecationWarning, match="files.mkdir"):
        result = shim.get_remote_dir("module_results/demo", parents=True)
    shim.files.mkdir.assert_called_once_with("module_results/demo", parents=True)
    assert result == PurePosixPath("module_results/demo")


def test_get_remote_dir_defaults_parents_false(shim):
    shim.files.mkdir.return_value = PurePosixPath("d")
    with pytest.warns(DeprecationWarning):
        shim.get_remote_dir("d")
    shim.files.mkdir.assert_called_once_with("d", parents=False)


def test_set_file_delegates_and_returns_dict(shim):
    shim.files.write.return_value = FileWriteResult(path="/x/a.js", size=3)
    with pytest.warns(DeprecationWarning, match="files.write"):
        result = shim.set_file("/x/a.js", "abc", overwrite=True)
    shim.files.write.assert_called_once_with("/x/a.js", "abc", overwrite=True)
    assert result == {"path": "/x/a.js", "size": 3}


def test_set_file_accepts_bytes_and_defaults_overwrite_false(shim):
    shim.files.write.return_value = FileWriteResult(path="/x/a.bin", size=2)
    with pytest.warns(DeprecationWarning):
        result = shim.set_file("/x/a.bin", b"hi")
    shim.files.write.assert_called_once_with("/x/a.bin", b"hi", overwrite=False)
    assert isinstance(result, dict)


def test_list_files_returns_legacy_dict_shape(shim):
    shim.files.list.return_value = DirectoryListing(
        path="/results",
        files=[FileEntry(name="a.js", path="/results/a.js", type="file", size=3)],
        count=1,
    )
    with pytest.warns(DeprecationWarning, match="files.list"):
        result = shim.list_files(folder="/results")
    shim.files.list.assert_called_once_with("/results", extensions=None)
    # sepal-gee-bundle does response.get("files", []) then item["name"]
    assert isinstance(result, dict)
    assert [f["name"] for f in result["files"]] == ["a.js"]


def test_session_manager_constructs_the_compat_client():
    import pysepal.solara.session_manager as session_manager

    assert session_manager.SepalClient is SepalClient


def test_get_file_parse_json_delegates_to_read_json(shim):
    shim.files.read_json.return_value = {"a": 1}
    with pytest.warns(DeprecationWarning, match="read_json"):
        result = shim.get_file("/x/a.json", parse_json=True)
    shim.files.read_json.assert_called_once_with("/x/a.json")
    assert result == {"a": 1}


def test_get_file_bytes_delegates_to_read_bytes(shim):
    shim.files.read_bytes.return_value = b"data"
    with pytest.warns(DeprecationWarning, match="read_bytes"):
        result = shim.get_file("/x/a.bin")
    shim.files.read_bytes.assert_called_once_with("/x/a.bin")
    assert result == b"data"
