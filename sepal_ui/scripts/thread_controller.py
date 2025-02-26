"""Controller for running long-running tasks in a separate thread."""

import threading
from typing import Callable, List, Optional

import sepal_ui.sepalwidgets as sw


class TaskController:
    def __init__(
        self,
        function: Callable,
        callback: Optional[Callable] = None,
        alert: Optional[sw.Alert] = None,
        start_button: Optional[sw.Btn] = None,
        stop_button: Optional[sw.Btn] = None,
        disable_components: Optional[List] = None,
        *function_args,
        **function_kwargs,
    ):
        """Initializes the TaskController.

        Args:
            function: The long-running function to execute.
            callback: A function to call with the result after the task completes.
            alert: An optional alert widget for displaying messages.
            start_button: An optional button to start the task.
            stop_button: An optional button to stop the task.
            disable_components: A list of components to disable while the task is running.
            *function_args: Positional arguments for the function.
            **function_kwargs: Keyword arguments for the function.
        """
        self.alert = alert
        self.function = function
        self.function_args = function_args
        self.function_kwargs = function_kwargs
        self.callback = callback
        self.disable_components = disable_components or []

        self.start_button = start_button
        self.stop_button = stop_button

        self.task_thread = None
        self.stop_event = threading.Event()

        # Set up event handlers if buttons are provided
        if self.start_button is not None:
            self.start_button.on_event("click", self.start_task)
        if self.stop_button is not None:
            self.stop_button.on_event("click", self.stop_task)

    def start_task(self, *args):
        """Starts the long-running task in a separate thread."""
        if self.task_thread is not None and self.task_thread.is_alive():
            # Task is already running
            return

        try:
            # Clear the stop event
            self.stop_event.clear()

            # Disable components
            self.set_components_enabled(False)

            # Reset the alert if provided
            if self.alert is not None:
                self.alert.reset()

            # Start the task thread
            self.task_thread = threading.Thread(target=self._run_task)
            self.task_thread.start()

        except Exception as e:
            print(f"Exception in start_task: {e}")

    def _run_task(self):
        """Runs the long-running task and handles completion."""
        try:
            if self.start_button is not None:
                self.start_button.loading = True

            # Run the user's function
            result = self.function(*self.function_args, **self.function_kwargs)

            # Call the callback with the result, if provided
            if self.callback:
                self.callback(result)

        except Exception as e:
            # Handle exceptions and display an error message
            print(f"Exception in _run_task: {e}")
            if self.alert is not None:
                self.alert.append_msg(f"Error occurred: {e}", type_="error")
        finally:
            # Re-enable components
            self.set_components_enabled(True)

            if self.start_button is not None:
                self.start_button.loading = False
            if self.stop_button is not None:
                self.stop_button.loading = False

    def stop_task(self, *args):
        """Signals the task to stop."""
        if self.stop_button is not None:
            self.stop_button.loading = True

        # Signal the task to stop
        self.stop_event.set()

        if self.alert is not None:
            self.alert.append_msg("The process was interrupted by the user.", type_="warning")

    def set_components_enabled(self, enabled: bool):
        """Enables or disables UI components."""
        for component in self.disable_components:
            component.disabled = not enabled
