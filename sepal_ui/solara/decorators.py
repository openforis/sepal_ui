"""Decorators for working with GEE interfaces in Solara applications.

This module provides decorators that can be used to automatically
handle GEE interface initialization and error handling in Solara components.
"""

import logging
from functools import wraps
from typing import Any, Callable, Optional

import solara
from eeclient.exceptions import EEClientError
from solara.lab import headers

from sepal_ui.solara.session_manager import SessionManager

logger = logging.getLogger("sepalui.solara.decorators")


def with_sepal_sessions(
    show_loading: bool = True,
    waiting_message: str = "Waiting for authentication headers...",
    module_name: str = "default",
    error_handler: Optional[Callable[[Exception], None]] = None,
):
    """Decorator that ensures a GEE interface is available before running the Solara Page component.

    Args:
        show_loading: Whether to show loading messages when session is not ready.
        waiting_message: Message to show when waiting for headers.
        module_name: The module name for the SepalClient.
        error_handler: Custom error handler function. If None, uses default error handling.

    Returns:
        Decorator function.

    Example:
        ```python
        @with_sepal_sessions(module_name="my.module")
        def Page():
            gee_interface = get_current_gee_interface()
            sepal_client = get_current_sepal_client()

            # Your component logic here
            solara.Markdown("GEE interface is ready!")
        ```
    """

    def decorator(component_func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(component_func)
        def wrapper(*args, **kwargs):
            # Check if headers are available first
            current_headers = headers.value
            if current_headers is None:
                if show_loading:
                    solara.Info(waiting_message)
                return

            # Try to create session and handle errors
            try:
                session_manager = SessionManager()
                session_manager.create_session(module_name=module_name)

                # Session is ready, call the component
                return component_func(*args, **kwargs)

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
