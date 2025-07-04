"""Custom Buttons.

Gather the customized ``ipyvuetifyWidgets`` used to create buttons.
All the content of this modules is included in the parent ``sepal_ui.sepalwidgets`` package. So it can be imported directly from there.

Example:
    .. jupyter-execute::

        from sepal_ui import sepalwidgets as sw

        sw.Btn()
"""

import warnings
from pathlib import Path
from typing import Any, Callable, Optional, Union

import ipyvuetify as v
import traitlets as t
from deprecated.sphinx import deprecated
from traitlets import observe
from typing_extensions import Self

from sepal_ui.scripts import utils as su
from sepal_ui.scripts.gee_task import GEETask
from sepal_ui.sepalwidgets.sepalwidget import SepalWidget

__all__ = ["Btn", "DownloadBtn", "TaskButton"]


class Btn(v.Btn, SepalWidget):

    v_icon: Optional[v.Icon] = None
    "the icon in the btn"

    gliph: t.Unicode = t.Unicode("").tag(sync=True)
    "the name of the icon"

    msg: t.Unicode = t.Unicode("").tag(sync=True)
    "the text of the btn"

    def __init__(self, msg: str = "", gliph: str = "", **kwargs) -> None:
        """Custom process Btn filled with the provided text.

        The color will be defaulted to 'primary' and can be changed afterward according to your need.

        Args:
            msg: the text to display in the btn
            gliph: the full name of any mdi/fa icon
            text: the text to display in the btn
            icon: the full name of any mdi/fa icon
            kwargs (dict, optional): any parameters from v.Btn. if set, 'children' will be overwritten.

        .. deprecated:: 2.13
            ``text`` and ``icon`` will be replaced by ``msg`` and ``gliph`` to avoid duplicating ipyvuetify trait.

        .. deprecated:: 2.14
            Btn is not using a default ``msg`` anymor`.
        """
        # deprecation in 2.13 of text and icon
        # as they already exist in the ipyvuetify Btn traits (as booleans)
        if "text" in kwargs:
            if isinstance(kwargs["text"], str):
                msg = kwargs.pop("text")
                warnings.warn('"text" is deprecated, please use "msg" instead', DeprecationWarning)
        if "icon" in kwargs:
            if isinstance(kwargs["icon"], str):
                gliph = kwargs.pop("icon")
                warnings.warn(
                    '"icon" is deprecated, please use "gliph" instead',
                    DeprecationWarning,
                )

        # create the default v_icon (hidden)
        self.v_icon = v.Icon(children=[""], left=True)
        self.v_icon.hide()

        # set the default parameters
        kwargs.setdefault("color", "primary")
        kwargs["children"] = [self.v_icon, self.msg]

        # call the constructor
        super().__init__(**kwargs)

        # set msg and gliph to trigger the rendering
        self.msg = msg
        self.gliph = gliph

    @observe("gliph")
    def _set_gliph(self, change: dict) -> Self:
        """Set a new icon. If the icon is set to "", then it's hidden."""
        self.v_icon.children = [self.gliph]
        self.v_icon.hide() if self.gliph == "" else self.v_icon.show()

        return self

    @observe("msg")
    def _set_text(self, change: dict) -> Self:
        """Set the text of the btn."""
        self.v_icon.left = bool(self.msg)
        self.children = [self.v_icon, self.msg]

        return self

    @deprecated(version="2.14", reason="Replace by the private _set_gliph")
    def set_icon(self, icon: str = "") -> Self:
        """Set a new icon. If the icon is set to "", then it's hidden.

        Args:
            icon: the full name of a mdi/fa icon
        """
        self.gliph = icon
        return self

    def toggle_loading(self) -> Self:
        """Jump between two states : disabled and loading - enabled and not loading."""
        self.loading = not self.loading
        self.disabled = self.loading

        return self


class DownloadBtn(v.Btn, SepalWidget):
    def __init__(self, text: str, path: Union[str, Path] = "#", **kwargs) -> None:
        """Custom download Btn filled with the provided text.

        The download icon is automatically embedded and green. The btn only accepts absolute links, if non is provided then the btn stays disabled.

        Args:
            text: the message inside the btn
            path: the absoluteor relative path to a downloadable content
            kwargs: any parameter from a v.Btn. if set, 'children' and 'target' will be overwritten.
        """
        # create a download icon
        v_icon = v.Icon(left=True, children=["fa-solid fa-download"])

        # set default parameters
        kwargs.setdefault("class_", "ma-2")
        kwargs.setdefault("xs5", True)
        kwargs.setdefault("color", "success")
        kwargs["children"] = [v_icon, text]
        kwargs["target"] = "_blank"
        kwargs["attributes"] = {"download": None}

        # call the constructor
        super().__init__(**kwargs)

        # create the URL
        self.set_url(path)

    def set_url(self, path: Union[str, Path] = "#") -> Self:
        """Set the URL of the download btn. and unable it.

        If nothing is provided the btn is disabled.

        Args:
            path: the absolute path to a downloadable content
        """
        # set the url
        url = su.create_download_link(path)
        self.href = url

        # unable or disable the btn
        self.disabled = str(path) == "#"

        # set the download attribute
        name = None if str(path) == "#" else Path(path).name
        self.attributes = {"download": name}

        return self


class TaskButton(v.VuetifyTemplate):
    """Custom toggle button using a to start and cancel a task."""

    original_text = t.Unicode("Start Task").tag(sync=True)
    cancel_text = t.Unicode("Cancel").tag(sync=True)
    original_color = t.Unicode("primary").tag(sync=True)
    cancel_color = t.Unicode("error").tag(sync=True)
    original_icon = t.Unicode("").tag(sync=True)
    cancel_icon = t.Unicode("mdi-close").tag(sync=True)
    is_running = t.Bool(False).tag(sync=True)
    show_loading = t.Bool(True).tag(sync=True)
    disabled = t.Bool(False).tag(sync=True)

    # Size properties
    small = t.Bool(False).tag(sync=True)
    x_small = t.Bool(False).tag(sync=True)
    large = t.Bool(False).tag(sync=True)
    x_large = t.Bool(False).tag(sync=True)

    template_file = t.Unicode(str(Path(__file__).parent / "vue/TaskButton.vue")).tag(sync=True)

    def __init__(
        self,
        label: str = "Start Task",
        cancel_text: str = "Cancel",
        original_color: str = "primary",
        cancel_color: str = "error",
        original_icon: str = "",
        cancel_icon: str = "mdi-close",
        show_loading: bool = True,
        small: bool = False,
        x_small: bool = False,
        large: bool = False,
        x_large: bool = False,
        **kwargs,
    ):
        """Initialize the TaskButton with Vue component.

        Args:
            label: Initial button text
            cancel_text: Text to show when task is running
            original_color: Button color when not running
            cancel_color: Button color when running
            original_icon: Icon when not running
            cancel_icon: Icon when running
            show_loading: Whether to show loading spinner when running
            small: Make button small
            x_small: Make button extra small
            large: Make button large
            x_large: Make button extra large
            **kwargs: Additional VuetifyTemplate arguments
        """
        # Task management
        self._task_factory: Optional[Callable[[], GEETask[Any]]] = None
        self._start_args = ()
        self._start_kwargs = {}
        self._task: Optional[GEETask[Any]] = None

        # Set initial properties
        self.original_text = label
        self.cancel_text = cancel_text
        self.original_color = original_color
        self.cancel_color = cancel_color
        self.original_icon = original_icon
        self.cancel_icon = cancel_icon
        self.show_loading = show_loading
        self.small = small
        self.x_small = x_small
        self.large = large
        self.x_large = x_large

        super().__init__(**kwargs)

    def vue_on_click_python(self, *args):
        """Handle button click from Vue component."""
        if self.is_running:
            self._on_cancel()
        else:
            self._on_start()

    def configure(
        self,
        task_factory: Callable[[], GEETask[Any]],
        start_args: tuple = (),
        start_kwargs: dict = None,
    ):
        """Provide (or update) the factory and args for the task anytime before starting."""
        self._task_factory = task_factory
        self._start_args = start_args
        self._start_kwargs = start_kwargs or {}

    def _on_start(self):
        """Start the task and update UI to cancel mode."""
        if not self._task_factory:
            raise RuntimeError("TaskButton not configured with a task_factory")

        self._task = self._task_factory()
        self.is_running = True

        original_on_finally = self._task._finally_callback

        def combined_on_finally():
            if original_on_finally:
                original_on_finally()
            self._on_finally()

        self._task._finally_callback = combined_on_finally

        self._task.start(*self._start_args, **self._start_kwargs)

    def _on_cancel(self):
        """Cancel the running task."""
        if self._task:
            self._task.cancel()

    def _on_finally(self):
        """Reset UI to original state - always runs at the end."""
        self.is_running = False
        self._task = None

    @property
    def children(self):
        """Expose the Vue component itself."""
        return self
