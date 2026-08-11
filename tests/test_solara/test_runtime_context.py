"""Tests for pysepal Solara runtime scope identity resolution.

``resolve_scope_id`` is a thin adapter over ``solara.scope.get_kernel_id``
(Solara's own Solara-server-or-IPython resolver), so these tests cover the
adapter contract: pass-through of the resolved id and translation of Solara's
failure modes into ``UnsupportedSolaraRuntimeError``.
"""

from unittest.mock import patch

import pytest
from traitlets.config import Config

from pysepal.solara.runtime_context import (
    PROCESS_SCOPE,
    UnsupportedSolaraRuntimeError,
    current_scope_id,
    resolve_scope_id,
)


def test_resolve_scope_id_delegates_to_solara_scope():
    with patch("solara.scope.get_kernel_id", return_value="kernel-uuid") as get_kernel_id:
        assert resolve_scope_id() == "kernel-uuid"
        get_kernel_id.assert_called_once_with(ipython_fallback=True)


def test_resolve_scope_id_raises_typed_error_when_no_runtime():
    with patch("solara.scope.get_kernel_id", side_effect=RuntimeError("Not in a kernel")):
        with pytest.raises(UnsupportedSolaraRuntimeError, match="No supported"):
            resolve_scope_id()


def test_resolve_scope_id_raises_typed_error_on_unparseable_connection_file():
    # solara.scope.get_kernel_id() regex-parses the ipykernel connection filename
    # and raises AttributeError when it does not match (e.g. non-standard kernel
    # launchers); degrade cleanly to "unsupported" instead of crashing render.
    err = AttributeError("'NoneType' object has no attribute 'group'")
    with patch("solara.scope.get_kernel_id", side_effect=err):
        with pytest.raises(UnsupportedSolaraRuntimeError, match="No supported"):
            resolve_scope_id()


def test_current_scope_id_falls_back_to_the_process_scope():
    """Scripts and pytest have no per-connection runtime; state still needs a key."""
    with patch("solara.scope.get_kernel_id", side_effect=RuntimeError("Not in a kernel")):
        assert current_scope_id() == PROCESS_SCOPE


class _FakeKernel:
    def __init__(self, config):
        self.config = config


class _FakeIPython:
    """Enough of an IPython shell for solara's ``ipython_fallback`` branch."""

    def __init__(self, config):
        self.kernel = _FakeKernel(config)


@pytest.mark.parametrize(
    ("name", "config"),
    [
        # traitlets auto-vivifies the missing key into a LazyConfigValue, so
        # solara's re.search() gets a non-string and raises TypeError.
        ("traitlets_config", Config()),
        # A mapping that does not auto-vivify raises KeyError instead.
        ("plain_dict", {"IPKernelApp": {}}),
    ],
)
def test_a_kernel_without_a_connection_file_is_an_unsupported_runtime(name, config):
    """Drive solara's real resolver, not a mocked exception.

    An embedded or in-process kernel presents ``ipython.kernel`` with no
    standard connection file. Mocking the exception type is what let this
    escape once already, so build the real config shapes and let
    ``solara.scope.get_kernel_id`` fail on its own terms.
    """
    with patch("IPython.get_ipython", return_value=_FakeIPython(config)):
        with pytest.raises(UnsupportedSolaraRuntimeError, match="No supported"):
            resolve_scope_id()


@pytest.mark.parametrize(
    ("name", "config"),
    [
        ("traitlets_config", Config()),
        ("plain_dict", {"IPKernelApp": {}}),
    ],
)
def test_current_scope_id_is_total_against_a_broken_kernel(name, config):
    """``current_scope_id`` promises a scope id *always*; a broken kernel is no exception.

    ``use_notifications`` and ``notify`` degrade to a no-op when no bus can be
    resolved, but only if resolution fails cleanly instead of raising through
    the render path.
    """
    with patch("IPython.get_ipython", return_value=_FakeIPython(config)):
        assert current_scope_id() == PROCESS_SCOPE
