"""Decorators for working with GEE interfaces in Solara applications.

This module provides decorators that can be used to automatically
handle GEE interface initialization and error handling in Solara components.
"""

import logging
from functools import wraps
from typing import Any, Callable, Optional

import solara
from eeclient.exceptions import EEClientError

from pysepal.solara.errors import SepalSessionError
from pysepal.solara.session_manager import SessionManager

logger = logging.getLogger("sepalui.solara.decorators")


def with_sepal_sessions(
    module_name: str = "default",
    error_handler: Optional[Callable[[Exception], None]] = None,
):
    """Decorator that establishes this runtime's session before the Page renders.

    **Required under an app-launcher Solara server, optional everywhere else.**
    There the session is per connection, built from that connection's SEPAL
    headers, and those are readable only on a thread carrying that connection's
    kernel context -- the render thread and any thread started from it, but not
    a thread-pool worker. Nothing can build one lazily, so
    ``get_current_gee_interface()`` raises ``SepalSessionError`` on a connection
    whose Page never ran the decorator. It is keyed by connection rather than by
    route: in a multipage app an undecorated route reuses the session a
    decorated one established.

    In a SEPAL sandbox, under Voila, in plain Jupyter, in a script, or wherever
    ``PYSEPAL_DEV_AUTH`` is armed, the session belongs to the process and the
    first ``get_current_*`` call builds it. Two reasons to write the decorator
    there anyway:

    - It sets the default ``module_name``. An accessor may still pass one per
      call, but only the decorator makes the choice stick for the bare calls
      afterwards; without it they get ``"default"``.
    - It wraps the whole render -- the session build *and* the component body --
      so any exception becomes a ``solara.Error`` in the page, or reaches
      ``error_handler``. That breadth has a cost: a body that raises after
      calling hooks is swallowed here, and reacton then reports a misleading
      "Previously render had N effects" hook-count error next to the alert.

    The credential source follows runtime topology, never header probing; see
    :mod:`pysepal.solara._topology` for the rules and their limits.

    Args:
        module_name: The module name for the SepalClient.
        error_handler: Custom error handler function. If None, uses default error handling.

    Returns:
        Decorator function.

    Example:
        .. code-block:: python

            @solara.component
            @with_sepal_sessions(module_name="my.module")
            def Page():
                gee_interface = get_current_gee_interface()
                sepal_client = get_current_sepal_client()

                solara.Markdown("GEE interface is ready!")
    """

    def decorator(component_func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(component_func)
        def wrapper(*args, **kwargs):
            try:
                session_manager = SessionManager()
                session_manager.create_session(module_name=module_name)

                return component_func(*args, **kwargs)

            except SepalSessionError as e:
                logger.error(f"SEPAL session error in {component_func.__name__}: {e}")
                if error_handler:
                    error_handler(e)
                else:
                    with solara.Error():
                        solara.Markdown(str(e))
                return

            except EEClientError as e:
                logger.error(f"GEE authentication error in {component_func.__name__}: {e}")
                if error_handler:
                    error_handler(e)
                else:
                    with solara.Error():
                        solara.Markdown(e.message)
                return

            except Exception as e:
                logger.error(f"Unexpected error in {component_func.__name__}: {e}", exc_info=True)
                if error_handler:
                    error_handler(e)
                else:
                    with solara.Error():
                        solara.Markdown(f"An error has occurred: {e}")
                return

        return wrapper

    return decorator
