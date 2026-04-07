"""Decorators used in sepal-ui.

used for multiple use-case sucha as (but not limited):
- catch errors in scripts to avoid Voila app freeze
- redirect error to a specific Alert object
- Initialize EE
- debug widgets
...
"""

import logging
import warnings
from functools import wraps
from itertools import product
from typing import Any, List, Optional
from warnings import warn

import ipyvuetify as v
from deprecated.sphinx import versionadded

from pysepal.message import ms
from pysepal.scripts.gee import init_ee, need_ee  # noqa: F401 - backward compatibility
from pysepal.scripts.warning import SepalWarning

_decorator_logger = logging.getLogger(__name__)


def _get_notification_bus():
    """Try to get the current notification bus. Returns None if unavailable."""
    try:
        from pysepal.solara.notifications.bus import get_current_bus

        return get_current_bus()
    except ImportError:
        return None


@versionadded(version="3.0", reason="moved from utils to a dedicated module")
def catch_errors(func=None, alert: Optional[v.Alert] = None, debug: Optional[bool] = None) -> Any:
    """Decorator to execute try/except sentence and catch errors.

    When alert= is provided or self.alert exists, uses legacy alert widget behavior.
    Otherwise, publishes to the notification bus (if mounted).

    Supports both @catch_errors and @catch_errors(alert=...) syntax.

    Args:
        func: The decorated function (when used without parentheses)
        alert: Alert to display errors (legacy, optional)
        debug: Deprecated, will be removed in v3.2

    Returns:
        The return statement of the decorated method
    """
    if debug is not None:
        warn("debug argument defaults to `True`. It will be removed in v3.2")

    def decorator_alert_error(func):
        @wraps(func)
        def wrapper_alert_error(self, *args, **kwargs):
            # Resolve alert: explicit param > self.alert > None
            alert_ = alert if alert else getattr(self, "alert", None)

            # If we have a legacy alert widget, use old behavior
            if alert_ is not None:
                alert_.reset()
                value = None
                try:
                    with warnings.catch_warnings(record=True) as w_list:
                        value = func(self, *args, **kwargs)

                    if w_list:
                        w_list_sepal = [w for w in w_list if isinstance(w.message, SepalWarning)]
                        ms_list = [
                            f"{w.category.__name__}: {w.message.args[0]}" for w in w_list_sepal
                        ]
                        [alert_.append_msg(ms, type_="warning") for ms in ms_list]

                        def custom_showwarning(w):
                            return warnings.showwarning(
                                message=w.message,
                                category=w.category,
                                filename=w.filename,
                                lineno=w.lineno,
                                line=w.line,
                            )

                        [custom_showwarning(w) for w in w_list]

                except Exception as e:
                    alert_.add_msg(f"{e}", type_="error")
                    raise e

                return value

            # No legacy alert — use notification bus
            bus = _get_notification_bus()
            value = None
            try:
                with warnings.catch_warnings(record=True) as w_list:
                    value = func(self, *args, **kwargs)

                if w_list and bus is not None:
                    from pysepal.solara.notifications.state import Toast, ToastType

                    w_list_sepal = [w for w in w_list if isinstance(w.message, SepalWarning)]
                    for w in w_list_sepal:
                        bus.add_toast(
                            Toast(
                                message=f"{w.category.__name__}: {w.message.args[0]}",
                                type=ToastType.WARNING,
                            )
                        )

                    def custom_showwarning(w):
                        return warnings.showwarning(
                            message=w.message,
                            category=w.category,
                            filename=w.filename,
                            lineno=w.lineno,
                            line=w.line,
                        )

                    [custom_showwarning(w) for w in w_list]

            except Exception as e:
                if bus is not None:
                    from pysepal.solara.notifications.state import Toast, ToastType

                    bus.add_toast(Toast(message=str(e), type=ToastType.ERROR))
                else:
                    _decorator_logger.error(f"Unhandled error (no alert or bus): {e}")
                raise e

            return value

        return wrapper_alert_error

    # Support both @catch_errors and @catch_errors(alert=...)
    if func is not None:
        return decorator_alert_error(func)
    return decorator_alert_error


@versionadded(version="3.0", reason="moved from utils to a dedicated module")
def loading_button(
    alert: Optional[v.Alert] = None,
    button: Optional[v.Btn] = None,
    debug: Optional[bool] = None,
) -> Any:
    """Decorator to execute try/except sentence and toggle loading button object.

    Designed to work within the Tile object, or any object that have a self.btn and self.alert set.

    Args:
        button: Toggled button
        alert: the alert to display the error message
        debug: Whethers or not the exception should stop the execution. default to False

    Returns:
        The return statement of the decorated method
    """
    if debug is not None:
        warn("debug argument defaults to `True`. It will be removed in v3.2")

    def decorator_loading(func):
        @wraps(func)
        def wrapper_loading(self, *args, **kwargs):
            # set btn and alert
            # Change name of variable to assign it again in this scope
            # check if they exist in the parent object if alert is not set manually
            assert hasattr(self, "alert") or alert, ms.decorator.no_alert
            assert hasattr(self, "btn") or button, ms.decorator.no_button
            button_ = self.btn if not button else button
            alert_ = self.alert if not alert else alert

            # Clean previous loaded messages in alert
            alert_.reset()

            button_.toggle_loading()  # Start loading

            value = None

            try:
                # run the function using the catch_error decorator
                value = catch_errors(alert=alert_)(func)(self, *args, **kwargs)

            except Exception as e:
                button_.toggle_loading()
                raise e

            # normal behavior where we stop the loading state after the function is executed
            button_.toggle_loading()

            return value

        return wrapper_loading

    return decorator_loading


@versionadded(version="3.0", reason="moved from utils to a dedicated module")
def switch(
    *params, debug: bool = True, on_widgets: List[str] = [], targets: List[bool] = []
) -> Any:
    r"""Decorator to switch the state of input boolean parameters on class widgets or the class itself.

    If on_widgets is defined, it will switch the state of every widget
    parameter, otherwise it will change the state of the class (self). You can also set
    two decorators on the same function, one could affect the class and other the widgets.

    Args:
        \*params: any boolean parameter of a SepalWidget.
        debug: Whether trigger or not an Exception if the decorated function fails.
        on_widgets: List of widget names into the class
        targets: list of the target value (value that will be set on switch. default to the inverse of the current state.

    Returns:
        The return statement of the decorated method
    """

    def decorator_switch(func):
        @wraps(func)
        def wrapper_switch(self, *args, **kwargs):
            widgets_len = len(on_widgets)
            targets_len = len(targets)

            # sanity check on targets and on_widgets
            if widgets_len and targets_len:
                if widgets_len != targets_len:
                    raise IndexError(
                        f'the length of "on_widgets" ({widgets_len}) is different from the length of "targets" ({targets_len})'
                    )

            # create the list of target values based on the target list
            # or the initial values of the widgets params
            # The first one is taken as reference
            if not targets_len:
                w = getattr(self, on_widgets[0]) if widgets_len else self
                targets_ = [bool(getattr(w, p)) for p in params]
            else:
                targets_ = targets

            if widgets_len:
                # Verify that the input elements are strings
                wrong_types = [(w, type(w)) for w in on_widgets if not isinstance(w, str)]

                if len(wrong_types):
                    errors = [f"Received:{w_type} for widget: {w}." for w, w_type in wrong_types]

                    raise TypeError(
                        f"All on_widgets list elements has to be strings. [{' '.join(errors)}]"
                    )

                missing_widgets = [w for w in on_widgets if not hasattr(self, w)]

                if missing_widgets:
                    raise Exception(
                        f"The provided {missing_widgets} widget(s) does not exist in the current class"
                    )

                def w_assign(bool_targets):
                    params_targets = [(p, bool_targets[i]) for i, p in enumerate(params)]

                    for w_name, p_t in product(on_widgets, params_targets):
                        param, target = p_t
                        widget = getattr(self, w_name)
                        setattr(widget, param, target)

            else:

                def w_assign(bool_targets):
                    for i, p in enumerate(params):
                        setattr(self, p, bool_targets[i])

            # assgn the parameters to the target inverse
            w_assign([not t for t in targets_])

            # execute the function and catch errors
            try:
                func(self, *args, **kwargs)

            except Exception as e:
                if debug:
                    w_assign(targets_)
                    raise e

            # reassign the parameters to the targets
            w_assign(targets_)

        return wrapper_switch

    return decorator_switch
