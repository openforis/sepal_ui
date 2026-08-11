"""Runtime scope identity for pysepal Solara, Voila and notebook state.

A *scope id* names the runtime that owns a session, a UI state or a
notification bus: a Solara-server virtual kernel, a Voila or Jupyter kernel,
or the process itself when there is no per-connection runtime at all. One
name, one resolver -- ``kernel_id`` and ``runtime_id`` were the same value
under two other names.
"""

import solara.scope

PROCESS_SCOPE = "process"
"Scope id used when no per-connection runtime can be resolved."


class UnsupportedSolaraRuntimeError(RuntimeError):
    """Raised when pysepal cannot resolve a per-connection app runtime."""


def resolve_scope_id() -> str:
    """Return the current per-connection runtime's scope id.

    Thin adapter over Solara's own ``solara.scope.get_kernel_id`` resolver: it
    returns the Solara-server virtual-kernel id and otherwise falls back to the
    active IPython/ipykernel -- covering ``solara run``, Voila (including
    preheated kernels, which start before ``SERVER_SOFTWARE`` is set), and plain
    Jupyter Notebook/Lab. We deliberately do not reimplement that resolution; we
    only translate its failure modes -- no kernel at all, or an ipykernel whose
    connection filename it cannot parse -- into a typed error.

    Returns:
        The runtime's scope id.

    Raises:
        UnsupportedSolaraRuntimeError: No per-connection runtime is available.
    """
    try:
        return solara.scope.get_kernel_id(ipython_fallback=True)
    except (RuntimeError, AttributeError) as exc:
        raise UnsupportedSolaraRuntimeError(
            "No supported pysepal runtime context is available"
        ) from exc


def current_scope_id() -> str:
    """Return a scope id for the current runtime, always.

    Returns:
        The per-connection runtime's scope id, or :data:`PROCESS_SCOPE` when
        there is none (script, pytest, unsupported kernel).
    """
    try:
        return resolve_scope_id()
    except UnsupportedSolaraRuntimeError:
        return PROCESS_SCOPE
