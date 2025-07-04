"""Task management utilities for GEE operations."""

import asyncio
import traceback
from enum import Enum
from typing import Any, Callable, Coroutine, Generic, Optional, TypeVar

import traitlets
from traitlets import Bool, Float, HasTraits, Instance, Unicode, observe

from sepal_ui.logger import log as logger

# Type variable for generic result type
R = TypeVar("R")


class TaskState(Enum):
    NOTCALLED = "not_called"
    STARTING = "starting"
    WAITING = "waiting"
    RUNNING = "running"
    ERROR = "error"
    FINISHED = "finished"
    CANCELLED = "cancelled"

    def __str__(self):
        """Return a user-friendly string representation of the task state."""
        return self.value


class GEETask(HasTraits, Generic[R]):
    """Wrap an async coroutine in an observable, cancellable task with a final callback."""

    state = traitlets.Enum(
        values=list(TaskState),
        default_value=TaskState.NOTCALLED,
        help="Current state of the task",
    )
    error = Instance(Exception, allow_none=True, help="Exception raised during task, if any")
    result = traitlets.Any(default_value=None, help="Result of the task execution")
    progress = Float(
        default_value=0.0, min=0.0, max=1.0, help="Progress of the task, from 0.0 to 1.0"
    )
    message = Unicode(default_value="", help="Status message for the task")
    is_active = Bool(default_value=False, help="Whether the task is currently active")

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        function: Callable[..., Coroutine[Any, Any, R]],
        key: Optional[str] = None,
        on_finally: Optional[Callable[[], None]] = None,
    ):
        """Initialize the GEETask with an event loop, coroutine function, and optional key and final callback."""
        super().__init__()
        self.loop = loop
        self.function = function
        self.key = key or function.__name__
        self._future: Optional[asyncio.Future] = None
        self._finally_callback = on_finally

    @observe("state")
    def _on_state_change(self, change):
        """Handle state changes to update is_active flag."""
        new = change["new"]
        self.is_active = new in (
            TaskState.STARTING,
            TaskState.WAITING,
            TaskState.RUNNING,
        )

    def start(self, *args, **kwargs) -> asyncio.Future:
        """Schedule the wrapped coroutine on the provided loop."""
        # Reset state
        self.state = TaskState.STARTING
        self.error = None
        self.result = None
        self.progress = 0.0
        self.message = f"Starting task {self.key}"

        # Schedule execution
        future = asyncio.run_coroutine_threadsafe(self._run(*args, **kwargs), self.loop)
        self._future = future
        return future

    async def _run(self, *args, **kwargs) -> None:
        """Run the user-provided coroutine, handling state transitions and exceptions."""
        try:
            self.state = TaskState.WAITING
            self.message = f"{self.key}: waiting to start"

            self.state = TaskState.RUNNING
            self.message = f"{self.key}: running"

            # Execute the user-provided coroutine
            result = await self.function(*args, **kwargs)

            # Store result and update state
            self.result = result
            self.state = TaskState.FINISHED
            self.message = f"{self.key}: completed successfully"

        except asyncio.CancelledError:
            self.message = f"{self.key}: cancelled"
            self.state = TaskState.CANCELLED
            logger.info(f"Task {self.key} cancelled by user")

        except Exception as e:
            self.error = e
            self.message = f"{self.key}: error {e}"
            self.state = TaskState.ERROR
            logger.error(f"Error in task {self.key}: {e}")
            tb = traceback.format_exc()
            logger.debug(tb)

        finally:
            # Clean up future pointer
            self._future = None
            # Always call the final callback
            if callable(self._finally_callback):
                try:
                    self._finally_callback()
                except Exception as e:
                    logger.error(f"Final callback for task {self.key} raised: {e}")
                    logger.debug(traceback.format_exc())

    def cancel(self) -> None:
        """Cancel the running task."""
        if self._future and not self._future.done():
            self._future.cancel()

    @property
    def is_running(self) -> bool:
        """Check if the task is currently running."""
        return self.state in (
            TaskState.STARTING,
            TaskState.WAITING,
            TaskState.RUNNING,
        )

    @property
    def is_finished(self) -> bool:
        """Check if the task has finished successfully."""
        return self.state is TaskState.FINISHED

    @property
    def is_error(self) -> bool:
        """Check if the task encountered an error."""
        return self.state is TaskState.ERROR

    @property
    def is_cancelled(self) -> bool:
        """Check if the task was cancelled."""
        return self.state is TaskState.CANCELLED

    def __enter__(self):
        """Context manager entry, starts the task."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit, cancels the task if still running."""
        # Cancel if still running
        if self._future and not self._future.done():
            self._future.cancel()
        return False  # propagate exceptions
