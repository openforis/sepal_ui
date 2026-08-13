"""Which URL add_raster hands the browser for a kernel-local tile server.

``localtileserver`` autodetects a ``jupyter-server-proxy`` prefix whenever it
finds itself in a Jupyter kernel. Voila is a kernel but is not a jupyter-server,
so it never serves that route and the tiles 404. Passing the environment
variable through to ``TileClient`` gives the caller the empty string, the one
value that suppresses both the env read and the autodetect.
"""

from pathlib import Path

import pytest

from pysepal import mapping as sm
from pysepal.mapping.sepal_map import CLIENT_PREFIX_ENV_VAR

AUTODETECTED = "localtileserver-proxy/{port}"


@pytest.fixture(autouse=True)
def kernel_autodetects_a_proxy_prefix(monkeypatch):
    """Stand in for running inside a kernel, where the prefix is autodetected."""
    import localtileserver.configure as configure

    monkeypatch.setattr(configure, "autodetect_prefix", lambda namespace, **kwargs: AUTODETECTED)


def test_an_unset_variable_leaves_the_autodetected_prefix_in_place(byte: Path, monkeypatch) -> None:
    monkeypatch.delenv(CLIENT_PREFIX_ENV_VAR, raising=False)

    layer = sm.SepalMap().add_raster(byte, key="auto")

    assert "localtileserver-proxy" in layer.url


def test_a_defined_but_empty_variable_addresses_the_tile_server_directly(
    byte: Path, monkeypatch
) -> None:
    # the Voila case: no proxy route exists, so the autodetected one must not win
    monkeypatch.setenv(CLIENT_PREFIX_ENV_VAR, "")

    layer = sm.SepalMap().add_raster(byte, key="direct")

    assert "localtileserver-proxy" not in layer.url
    assert layer.url.startswith("http://127.0.0.1:")


def test_an_explicit_prefix_is_used_verbatim(byte: Path, monkeypatch) -> None:
    monkeypatch.setenv(CLIENT_PREFIX_ENV_VAR, "/api/sandbox/tiles/{port}")

    layer = sm.SepalMap().add_raster(byte, key="explicit")

    assert "/api/sandbox/tiles/" in layer.url
    assert "localtileserver-proxy" not in layer.url
