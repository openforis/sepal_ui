"""pysepal must import in an environment it cannot write to."""

import subprocess
import sys

import pytest


def test_conf_module_is_gone():
    with pytest.raises(ModuleNotFoundError):
        __import__("pysepal.conf")


def test_config_is_not_public_api():
    import pysepal

    assert not hasattr(pysepal, "config")
    assert not hasattr(pysepal, "config_file")


def test_config_writers_are_gone():
    from pysepal.scripts import utils as su

    for name in ("set_config", "_write_config", "set_config_locale", "set_config_theme"):
        assert not hasattr(su, name)


def test_import_succeeds_with_a_read_only_home(tmp_path):
    home = tmp_path / "home"
    home.mkdir(mode=0o500)
    env = {"HOME": str(home), "PATH": "/usr/bin:/bin"}
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import pysepal"],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0, result.stderr
        assert "PermissionError" not in result.stderr
    finally:
        home.chmod(0o700)


def test_import_creates_nothing_in_home(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    env = {"HOME": str(home), "PATH": "/usr/bin:/bin"}
    subprocess.run([sys.executable, "-c", "import pysepal"], check=True, env=env)
    assert list(home.iterdir()) == []
