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
    """Decorator that establishes a SEPAL session before the Page renders.

    The credential source follows runtime topology, never header probing. Under
    an app-launcher Solara server the session is built from this connection's
    SEPAL headers and missing or invalid ones are an error -- there is nothing
    else to fall back to that would still be this user. In a SEPAL sandbox,
    under Voila, in plain Jupyter or in a script the process session is used and
    no headers are involved.

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
