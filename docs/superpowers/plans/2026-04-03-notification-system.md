# Notification System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a two-layer notification system (toasts + task progress) that centralizes all notification UI into a single kernel-scoped provider, replacing per-component Alert/Banner/StateBar usage.

**Architecture:** A `NotificationBus` (keyed by Solara kernel ID, matching the existing `SessionManager` pattern) stores toast and task state. Components publish via a `use_notifications()` hook or `notify()` global function. A single `NotificationProvider` at the app root renders a floating `ToastStack` and `TaskProgressPill`.

**Tech Stack:** Solara, `reacton.ipyvuetify` (for Snackbar/transitions), `solara.reactive()`, `dataclasses`, `threading.Lock`

**Spec:** `docs/superpowers/specs/2026-04-03-notification-system-design.md`

---

### Task 1: Test Infrastructure and State Model

**Files:**

- Create: `tests/test_solara/__init__.py`
- Create: `tests/test_solara/test_notifications/__init__.py`
- Create: `tests/test_solara/test_notifications/test_state.py`
- Create: `pysepal/solara/notifications/__init__.py`
- Create: `pysepal/solara/notifications/state.py`

- [ ] **Step 1: Create test directory structure**

```bash
mkdir -p tests/test_solara/test_notifications
touch tests/test_solara/__init__.py
touch tests/test_solara/test_notifications/__init__.py
```

- [ ] **Step 2: Write failing tests for state model**

File: `tests/test_solara/test_notifications/test_state.py`

```python
"""Tests for notification state model (dataclasses, enums, defaults)."""

from dataclasses import replace

import pytest

from pysepal.solara.notifications.state import (
    TOAST_TIMEOUT_DEFAULTS,
    TaskMilestone,
    TaskStatus,
    Toast,
    ToastType,
    TrackedTask,
)


class TestToastType:
    def test_values(self):
        assert ToastType.SUCCESS.value == "success"
        assert ToastType.INFO.value == "info"
        assert ToastType.WARNING.value == "warning"
        assert ToastType.ERROR.value == "error"


class TestToastTimeoutDefaults:
    def test_success_timeout(self):
        assert TOAST_TIMEOUT_DEFAULTS[ToastType.SUCCESS] == 5.0

    def test_info_timeout(self):
        assert TOAST_TIMEOUT_DEFAULTS[ToastType.INFO] == 5.0

    def test_warning_timeout(self):
        assert TOAST_TIMEOUT_DEFAULTS[ToastType.WARNING] == 10.0

    def test_error_no_timeout(self):
        assert TOAST_TIMEOUT_DEFAULTS[ToastType.ERROR] is None


class TestTaskStatus:
    def test_all_values(self):
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"


class TestToast:
    def test_defaults(self):
        toast = Toast(message="hello")
        assert toast.message == "hello"
        assert toast.type == ToastType.INFO
        assert toast.timeout is None
        assert toast.count == 1
        assert toast.id  # non-empty UUID

    def test_frozen(self):
        toast = Toast(message="hello")
        with pytest.raises(AttributeError):
            toast.message = "world"

    def test_effective_timeout_uses_default(self):
        toast = Toast(message="ok", type=ToastType.SUCCESS)
        assert toast.effective_timeout() == 5.0

    def test_effective_timeout_uses_explicit(self):
        toast = Toast(message="ok", type=ToastType.SUCCESS, timeout=20.0)
        assert toast.effective_timeout() == 20.0

    def test_effective_timeout_error_is_none(self):
        toast = Toast(message="bad", type=ToastType.ERROR)
        assert toast.effective_timeout() is None

    def test_unique_ids(self):
        t1 = Toast(message="a")
        t2 = Toast(message="b")
        assert t1.id != t2.id

    def test_replace_count(self):
        toast = Toast(message="a", count=1)
        updated = replace(toast, count=2)
        assert updated.count == 2
        assert toast.count == 1  # original unchanged


class TestTaskMilestone:
    def test_defaults(self):
        ms = TaskMilestone(message="step 1")
        assert ms.message == "step 1"
        assert ms.timestamp > 0

    def test_frozen(self):
        ms = TaskMilestone(message="step 1")
        with pytest.raises(AttributeError):
            ms.message = "step 2"


class TestTrackedTask:
    def test_defaults(self):
        task = TrackedTask(title="Processing")
        assert task.title == "Processing"
        assert task.status == TaskStatus.PENDING
        assert task.milestones == ()
        assert task.progress is None
        assert task.total_steps is None
        assert task.current_step == 0
        assert task.error_message is None

    def test_frozen(self):
        task = TrackedTask(title="Processing")
        with pytest.raises(AttributeError):
            task.status = TaskStatus.RUNNING

    def test_add_milestone_via_replace(self):
        task = TrackedTask(title="Processing")
        ms = TaskMilestone(message="step 1")
        updated = replace(task, milestones=(*task.milestones, ms), current_step=1)
        assert len(updated.milestones) == 1
        assert updated.current_step == 1
        assert task.milestones == ()  # original unchanged

    def test_update_progress_via_replace(self):
        task = TrackedTask(title="Processing")
        updated = replace(task, progress=0.5)
        assert updated.progress == 0.5
        assert task.progress is None

    def test_unique_ids(self):
        t1 = TrackedTask(title="a")
        t2 = TrackedTask(title="b")
        assert t1.id != t2.id
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/test_solara/test_notifications/test_state.py -v`
Expected: `ModuleNotFoundError: No module named 'pysepal.solara.notifications'`

- [ ] **Step 4: Implement state model**

File: `pysepal/solara/notifications/__init__.py`

```python
"""Centralized notification system for pysepal Solara applications."""
```

File: `pysepal/solara/notifications/state.py`

```python
"""Notification state model: dataclasses, enums, and defaults."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time
import uuid


class ToastType(Enum):
    """Type of toast notification, determines color and auto-dismiss behavior."""

    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


TOAST_TIMEOUT_DEFAULTS: dict[ToastType, Optional[float]] = {
    ToastType.SUCCESS: 5.0,
    ToastType.INFO: 5.0,
    ToastType.WARNING: 10.0,
    ToastType.ERROR: None,
}


class TaskStatus(Enum):
    """Lifecycle status of a tracked task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Toast:
    """An ephemeral notification message."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message: str = ""
    type: ToastType = ToastType.INFO
    created_at: float = field(default_factory=time.time)
    timeout: Optional[float] = None
    count: int = 1

    def effective_timeout(self) -> Optional[float]:
        """Return the timeout, falling back to the type default."""
        if self.timeout is not None:
            return self.timeout
        return TOAST_TIMEOUT_DEFAULTS.get(self.type)


@dataclass(frozen=True)
class TaskMilestone:
    """A discrete named step in a task's execution."""

    message: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class TrackedTask:
    """A long-running task being tracked in the progress panel."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    status: TaskStatus = TaskStatus.PENDING
    milestones: tuple[TaskMilestone, ...] = ()
    progress: Optional[float] = None
    total_steps: Optional[int] = None
    current_step: int = 0
    created_at: float = field(default_factory=time.time)
    error_message: Optional[str] = None
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_solara/test_notifications/test_state.py -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add pysepal/solara/notifications/__init__.py pysepal/solara/notifications/state.py \
       tests/test_solara/__init__.py tests/test_solara/test_notifications/__init__.py \
       tests/test_solara/test_notifications/test_state.py
git commit -m "feat(notifications): add state model with dataclasses and enums"
```

---

### Task 2: NotificationBus

**Files:**

- Create: `pysepal/solara/notifications/bus.py`
- Create: `tests/test_solara/test_notifications/test_bus.py`

- [ ] **Step 1: Write failing tests for NotificationBus**

File: `tests/test_solara/test_notifications/test_bus.py`

```python
"""Tests for NotificationBus: mutations, dedup, queue limits, thread safety."""

import time
import threading
from dataclasses import replace
from unittest.mock import MagicMock, patch

import pytest

from pysepal.solara.notifications.bus import (
    MAX_TOAST_QUEUE,
    DEDUP_WINDOW_SECONDS,
    NotificationBus,
    get_current_bus,
    create_bus,
    cleanup_bus,
    _buses,
    _get_kernel_id,
)
from pysepal.solara.notifications.state import (
    Toast,
    ToastType,
    TrackedTask,
    TaskStatus,
    TaskMilestone,
)


class TestNotificationBusToasts:
    def setup_method(self):
        self.bus = NotificationBus()

    def test_add_toast(self):
        toast = Toast(message="hello", type=ToastType.SUCCESS)
        self.bus.add_toast(toast)
        assert len(self.bus.toasts.value) == 1
        assert self.bus.toasts.value[0].message == "hello"

    def test_remove_toast(self):
        toast = Toast(message="hello")
        self.bus.add_toast(toast)
        self.bus.remove_toast(toast.id)
        assert len(self.bus.toasts.value) == 0

    def test_remove_nonexistent_toast_is_noop(self):
        self.bus.remove_toast("nonexistent-id")
        assert len(self.bus.toasts.value) == 0

    def test_dedup_merges_identical_toasts(self):
        now = time.time()
        t1 = Toast(message="dup", type=ToastType.INFO, created_at=now)
        t2 = Toast(message="dup", type=ToastType.INFO, created_at=now + 0.5)
        self.bus.add_toast(t1)
        self.bus.add_toast(t2)
        assert len(self.bus.toasts.value) == 1
        assert self.bus.toasts.value[0].count == 2

    def test_no_dedup_after_window(self):
        now = time.time()
        t1 = Toast(message="dup", type=ToastType.INFO, created_at=now)
        t2 = Toast(
            message="dup",
            type=ToastType.INFO,
            created_at=now + DEDUP_WINDOW_SECONDS + 1,
        )
        self.bus.add_toast(t1)
        self.bus.add_toast(t2)
        assert len(self.bus.toasts.value) == 2

    def test_no_dedup_different_type(self):
        now = time.time()
        t1 = Toast(message="msg", type=ToastType.INFO, created_at=now)
        t2 = Toast(message="msg", type=ToastType.ERROR, created_at=now)
        self.bus.add_toast(t1)
        self.bus.add_toast(t2)
        assert len(self.bus.toasts.value) == 2

    def test_queue_limit_drops_oldest_non_errors(self):
        for i in range(MAX_TOAST_QUEUE + 5):
            self.bus.add_toast(
                Toast(message=f"msg-{i}", type=ToastType.INFO, created_at=time.time() + i)
            )
        assert len(self.bus.toasts.value) <= MAX_TOAST_QUEUE

    def test_queue_limit_preserves_errors(self):
        # Fill with errors
        for i in range(MAX_TOAST_QUEUE):
            self.bus.add_toast(Toast(message=f"err-{i}", type=ToastType.ERROR))
        # Add one more info toast
        self.bus.add_toast(Toast(message="info", type=ToastType.INFO))
        # Errors should all be preserved
        errors = [t for t in self.bus.toasts.value if t.type == ToastType.ERROR]
        assert len(errors) == MAX_TOAST_QUEUE


class TestNotificationBusTasks:
    def setup_method(self):
        self.bus = NotificationBus()

    def test_add_task(self):
        task = TrackedTask(title="Processing")
        self.bus.add_task(task)
        assert len(self.bus.tasks.value) == 1
        assert self.bus.tasks.value[0].title == "Processing"

    def test_update_task(self):
        task = TrackedTask(title="Processing")
        self.bus.add_task(task)
        self.bus.update_task(task.id, status=TaskStatus.RUNNING, progress=0.5)
        updated = self.bus.tasks.value[0]
        assert updated.status == TaskStatus.RUNNING
        assert updated.progress == 0.5

    def test_update_nonexistent_task_is_noop(self):
        self.bus.update_task("nonexistent", status=TaskStatus.RUNNING)
        assert len(self.bus.tasks.value) == 0

    def test_remove_task(self):
        task = TrackedTask(title="Processing")
        self.bus.add_task(task)
        self.bus.remove_task(task.id)
        assert len(self.bus.tasks.value) == 0

    def test_add_milestone_via_update(self):
        task = TrackedTask(title="Processing")
        self.bus.add_task(task)
        ms = TaskMilestone(message="step 1")
        self.bus.update_task(
            task.id,
            milestones=(ms,),
            current_step=1,
            status=TaskStatus.RUNNING,
        )
        updated = self.bus.tasks.value[0]
        assert len(updated.milestones) == 1
        assert updated.milestones[0].message == "step 1"
        assert updated.current_step == 1


class TestNotificationBusThreadSafety:
    def test_concurrent_toast_adds(self):
        bus = NotificationBus()
        errors = []

        def add_toasts(start):
            try:
                for i in range(50):
                    bus.add_toast(
                        Toast(message=f"t-{start}-{i}", created_at=time.time() + start + i)
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=add_toasts, args=(n * 100,)) for n in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        # Should have added toasts without crashing (count capped by MAX_TOAST_QUEUE)
        assert len(bus.toasts.value) <= MAX_TOAST_QUEUE


class TestKernelRegistry:
    def setup_method(self):
        _buses.clear()

    def teardown_method(self):
        _buses.clear()

    @patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="kernel-1")
    def test_create_and_get_bus(self, mock_kid):
        bus = create_bus()
        assert isinstance(bus, NotificationBus)
        assert get_current_bus() is bus

    @patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="kernel-1")
    def test_cleanup_bus(self, mock_kid):
        create_bus()
        cleanup_bus()
        assert get_current_bus() is None

    @patch("pysepal.solara.notifications.bus._get_kernel_id")
    def test_different_kernels_get_different_buses(self, mock_kid):
        mock_kid.return_value = "kernel-1"
        bus1 = create_bus()
        mock_kid.return_value = "kernel-2"
        bus2 = create_bus()
        assert bus1 is not bus2
        mock_kid.return_value = "kernel-1"
        assert get_current_bus() is bus1

    def test_get_bus_returns_none_without_kernel_context(self):
        # No mock, so _get_kernel_id() will fail
        assert get_current_bus() is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_solara/test_notifications/test_bus.py -v`
Expected: `ModuleNotFoundError: No module named 'pysepal.solara.notifications.bus'`

- [ ] **Step 3: Implement NotificationBus**

File: `pysepal/solara/notifications/bus.py`

```python
"""Kernel-scoped notification bus: state management and registry."""

import logging
import threading
import time
from dataclasses import replace
from typing import Dict, Optional

import solara
import solara.server.kernel_context

from .state import Toast, ToastType, TrackedTask

logger = logging.getLogger(__name__)

MAX_TOAST_QUEUE = 20
DEDUP_WINDOW_SECONDS = 2.0


class NotificationBus:
    """Owns notification state for a single kernel/session.

    All mutations produce new list copies (never mutate in place).
    Thread-safe via internal lock.
    """

    def __init__(self):
        self.toasts: solara.Reactive[list[Toast]] = solara.reactive([])
        self.tasks: solara.Reactive[list[TrackedTask]] = solara.reactive([])
        self._lock = threading.Lock()

    def add_toast(self, toast: Toast) -> None:
        """Add a toast, applying dedup and queue limit rules."""
        with self._lock:
            current = list(self.toasts.value)

            # Dedup: merge if identical message+type within window
            for i, existing in enumerate(current):
                if (
                    existing.message == toast.message
                    and existing.type == toast.type
                    and (toast.created_at - existing.created_at) < DEDUP_WINDOW_SECONDS
                ):
                    current[i] = replace(existing, count=existing.count + 1)
                    self.toasts.value = current
                    return

            current.append(toast)

            # Enforce queue limit: drop oldest non-errors first
            if len(current) > MAX_TOAST_QUEUE:
                errors = [t for t in current if t.type == ToastType.ERROR]
                non_errors = [t for t in current if t.type != ToastType.ERROR]
                keep_non_errors = max(0, MAX_TOAST_QUEUE - len(errors))
                non_errors = non_errors[-keep_non_errors:] if keep_non_errors else []
                current = errors + non_errors

            self.toasts.value = current

    def remove_toast(self, toast_id: str) -> None:
        """Remove a toast by ID."""
        with self._lock:
            self.toasts.value = [t for t in self.toasts.value if t.id != toast_id]

    def add_task(self, task: TrackedTask) -> None:
        """Add a tracked task."""
        with self._lock:
            self.tasks.value = [*self.tasks.value, task]

    def update_task(self, task_id: str, **changes) -> None:
        """Update a tracked task by ID. Unknown IDs are silently ignored."""
        with self._lock:
            self.tasks.value = [
                replace(t, **changes) if t.id == task_id else t
                for t in self.tasks.value
            ]

    def remove_task(self, task_id: str) -> None:
        """Remove a tracked task by ID."""
        with self._lock:
            self.tasks.value = [t for t in self.tasks.value if t.id != task_id]


# --- Kernel-scoped bus registry (matches SessionManager pattern) ---

_buses: Dict[str, NotificationBus] = {}
_registry_lock = threading.Lock()


def _get_kernel_id() -> str:
    """Get current Solara kernel ID (same approach as SessionManager)."""
    return str(id(solara.server.kernel_context.get_current_context().kernel))


def get_current_bus() -> Optional[NotificationBus]:
    """Get the NotificationBus for the current kernel, or None."""
    try:
        kernel_id = _get_kernel_id()
    except Exception:
        return None
    with _registry_lock:
        return _buses.get(kernel_id)


def create_bus() -> NotificationBus:
    """Create and register a NotificationBus for the current kernel."""
    kernel_id = _get_kernel_id()
    bus = NotificationBus()
    with _registry_lock:
        _buses[kernel_id] = bus
    logger.debug(f"Created NotificationBus for kernel {kernel_id}")
    return bus


def cleanup_bus() -> None:
    """Remove the NotificationBus for the current kernel."""
    kernel_id = _get_kernel_id()
    with _registry_lock:
        removed = _buses.pop(kernel_id, None)
    if removed:
        logger.debug(f"Cleaned up NotificationBus for kernel {kernel_id}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_solara/test_notifications/test_bus.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add pysepal/solara/notifications/bus.py tests/test_solara/test_notifications/test_bus.py
git commit -m "feat(notifications): add kernel-scoped NotificationBus with dedup and queue limits"
```

---

### Task 3: Notifier and TaskTracker

**Files:**

- Create: `pysepal/solara/notifications/notifier.py`
- Create: `tests/test_solara/test_notifications/test_notifier.py`

- [ ] **Step 1: Write failing tests for Notifier and TaskTracker**

File: `tests/test_solara/test_notifications/test_notifier.py`

```python
"""Tests for Notifier (toast publishing) and TaskTracker (context manager)."""

import asyncio
import time

import pytest

from pysepal.solara.notifications.bus import NotificationBus
from pysepal.solara.notifications.notifier import Notifier, NoopNotifier
from pysepal.solara.notifications.state import (
    TaskStatus,
    ToastType,
)


class TestNotifier:
    def setup_method(self):
        self.bus = NotificationBus()
        self.notifier = Notifier(self.bus)

    def test_success(self):
        self.notifier.success("done!")
        assert len(self.bus.toasts.value) == 1
        assert self.bus.toasts.value[0].type == ToastType.SUCCESS
        assert self.bus.toasts.value[0].message == "done!"

    def test_error(self):
        self.notifier.error("failed!")
        assert self.bus.toasts.value[0].type == ToastType.ERROR

    def test_warning(self):
        self.notifier.warning("careful!")
        assert self.bus.toasts.value[0].type == ToastType.WARNING

    def test_info(self):
        self.notifier.info("fyi")
        assert self.bus.toasts.value[0].type == ToastType.INFO

    def test_dismiss(self):
        self.notifier.success("msg")
        toast_id = self.bus.toasts.value[0].id
        self.notifier.dismiss(toast_id)
        assert len(self.bus.toasts.value) == 0


class TestTaskTracker:
    def setup_method(self):
        self.bus = NotificationBus()
        self.notifier = Notifier(self.bus)

    def test_track_creates_task(self):
        with self.notifier.track("Processing") as task:
            assert len(self.bus.tasks.value) == 1
            assert self.bus.tasks.value[0].status == TaskStatus.RUNNING

    def test_track_auto_completes(self):
        with self.notifier.track("Processing"):
            pass
        assert self.bus.tasks.value[0].status == TaskStatus.COMPLETED

    def test_track_with_total_steps(self):
        with self.notifier.track("Processing", total_steps=3) as task:
            assert self.bus.tasks.value[0].total_steps == 3

    def test_step_adds_milestone(self):
        with self.notifier.track("Processing") as task:
            task.step("Validating...")
        milestones = self.bus.tasks.value[0].milestones
        assert len(milestones) == 1
        assert milestones[0].message == "Validating..."

    def test_step_increments_current_step(self):
        with self.notifier.track("Processing", total_steps=3) as task:
            task.step("Step 1")
            assert self.bus.tasks.value[0].current_step == 1
            task.step("Step 2")
            assert self.bus.tasks.value[0].current_step == 2

    def test_set_progress(self):
        with self.notifier.track("Processing") as task:
            task.set_progress(0.5)
        assert self.bus.tasks.value[0].progress == 0.5

    def test_set_progress_does_not_add_milestone(self):
        with self.notifier.track("Processing") as task:
            task.set_progress(0.5)
        assert len(self.bus.tasks.value[0].milestones) == 0

    def test_update_title(self):
        with self.notifier.track("Processing") as task:
            task.update("New title")
        assert self.bus.tasks.value[0].title == "New title"

    def test_explicit_complete(self):
        with self.notifier.track("Processing") as task:
            task.complete("All done")
        t = self.bus.tasks.value[0]
        assert t.status == TaskStatus.COMPLETED

    def test_explicit_fail(self):
        with self.notifier.track("Processing") as task:
            task.fail("Something broke")
        t = self.bus.tasks.value[0]
        assert t.status == TaskStatus.FAILED
        assert t.error_message == "Something broke"

    def test_explicit_cancel(self):
        with self.notifier.track("Processing") as task:
            task.cancel()
        assert self.bus.tasks.value[0].status == TaskStatus.CANCELLED

    def test_exception_marks_failed_and_publishes_error_toast(self):
        with pytest.raises(ValueError, match="boom"):
            with self.notifier.track("Processing") as task:
                task.step("Step 1")
                raise ValueError("boom")
        t = self.bus.tasks.value[0]
        assert t.status == TaskStatus.FAILED
        assert t.error_message == "boom"
        assert len(t.milestones) == 1  # Step history preserved
        # Error toast published
        assert len(self.bus.toasts.value) == 1
        assert self.bus.toasts.value[0].type == ToastType.ERROR

    def test_cancelled_error_maps_to_cancelled_status(self):
        with pytest.raises(asyncio.CancelledError):
            with self.notifier.track("Processing") as task:
                raise asyncio.CancelledError()
        assert self.bus.tasks.value[0].status == TaskStatus.CANCELLED
        # No error toast for cancellation
        assert len(self.bus.toasts.value) == 0

    def test_fail_does_not_double_complete(self):
        """If task already failed explicitly, __exit__ should not override."""
        with pytest.raises(RuntimeError):
            with self.notifier.track("Processing") as task:
                task.fail("manual fail")
                raise RuntimeError("also raises")
        assert self.bus.tasks.value[0].status == TaskStatus.FAILED
        assert self.bus.tasks.value[0].error_message == "manual fail"


class TestNoopNotifier:
    def test_noop_toast_methods(self):
        noop = NoopNotifier()
        # Should not raise
        noop.success("msg")
        noop.error("msg")
        noop.warning("msg")
        noop.info("msg")
        noop.dismiss("id")

    def test_noop_track_context_manager(self):
        noop = NoopNotifier()
        with noop.track("Processing") as task:
            task.step("step 1")
            task.set_progress(0.5)
        # Should not raise
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_solara/test_notifications/test_notifier.py -v`
Expected: `ModuleNotFoundError: No module named 'pysepal.solara.notifications.notifier'`

- [ ] **Step 3: Implement Notifier and TaskTracker**

File: `pysepal/solara/notifications/notifier.py`

```python
"""Publisher API: Notifier (toast methods) and TaskTracker (context manager)."""

import asyncio
import logging
from typing import Optional

from .bus import NotificationBus
from .state import (
    TaskMilestone,
    TaskStatus,
    Toast,
    ToastType,
    TrackedTask,
)

logger = logging.getLogger(__name__)


class TaskTracker:
    """Context manager for tracking a long-running task with milestones."""

    def __init__(self, bus: NotificationBus, task: TrackedTask):
        self._bus = bus
        self._task_id = task.id
        self._finished = False

    def step(self, message: str) -> None:
        """Add a named milestone and increment current_step."""
        if self._finished:
            return
        current = self._get_task()
        if current is None:
            return
        milestone = TaskMilestone(message=message)
        self._bus.update_task(
            self._task_id,
            milestones=(*current.milestones, milestone),
            current_step=current.current_step + 1,
            status=TaskStatus.RUNNING,
        )

    def set_progress(self, value: float) -> None:
        """Update continuous progress (0.0-1.0). Does NOT create a milestone."""
        if self._finished:
            return
        self._bus.update_task(self._task_id, progress=value)

    def update(self, title: str) -> None:
        """Update the task title."""
        if self._finished:
            return
        self._bus.update_task(self._task_id, title=title)

    def complete(self, message: Optional[str] = None) -> None:
        """Explicitly mark the task as completed."""
        if self._finished:
            return
        self._finished = True
        changes = {"status": TaskStatus.COMPLETED, "progress": 1.0}
        if message:
            changes["milestones"] = (
                *self._get_task().milestones,
                TaskMilestone(message=message),
            )
        self._bus.update_task(self._task_id, **changes)

    def fail(self, message: str) -> None:
        """Explicitly mark the task as failed."""
        if self._finished:
            return
        self._finished = True
        self._bus.update_task(
            self._task_id,
            status=TaskStatus.FAILED,
            error_message=message,
        )

    def cancel(self) -> None:
        """Explicitly mark the task as cancelled."""
        if self._finished:
            return
        self._finished = True
        self._bus.update_task(self._task_id, status=TaskStatus.CANCELLED)

    def _get_task(self) -> Optional[TrackedTask]:
        """Get the current task state from the bus."""
        for t in self._bus.tasks.value:
            if t.id == self._task_id:
                return t
        return None


class Notifier:
    """Main publisher API for notifications."""

    def __init__(self, bus: NotificationBus):
        self._bus = bus

    def success(self, message: str) -> None:
        """Publish a success toast."""
        self._bus.add_toast(Toast(message=message, type=ToastType.SUCCESS))

    def error(self, message: str) -> None:
        """Publish an error toast (persists until dismissed)."""
        self._bus.add_toast(Toast(message=message, type=ToastType.ERROR))

    def warning(self, message: str) -> None:
        """Publish a warning toast."""
        self._bus.add_toast(Toast(message=message, type=ToastType.WARNING))

    def info(self, message: str) -> None:
        """Publish an info toast."""
        self._bus.add_toast(Toast(message=message, type=ToastType.INFO))

    def dismiss(self, toast_id: str) -> None:
        """Dismiss a toast by ID."""
        self._bus.remove_toast(toast_id)

    def track(self, title: str, total_steps: Optional[int] = None) -> "TaskTracker":
        """Return a TaskTracker context manager for a long-running task."""
        task = TrackedTask(title=title, total_steps=total_steps)
        self._bus.add_task(task)
        return _TaskTrackerContextManager(self._bus, task)


class _TaskTrackerContextManager(TaskTracker):
    """TaskTracker that also acts as a context manager."""

    def __enter__(self) -> TaskTracker:
        self._bus.update_task(self._task_id, status=TaskStatus.RUNNING)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._finished:
            # Already explicitly completed/failed/cancelled
            if exc_type is not None:
                return False  # Re-raise
            return False

        if exc_type is None:
            self.complete()
        elif issubclass(exc_type, asyncio.CancelledError):
            self.cancel()
            return False  # Re-raise CancelledError
        else:
            self.fail(str(exc_val))
            # Publish error toast
            self._bus.add_toast(
                Toast(message=str(exc_val), type=ToastType.ERROR)
            )
            return False  # Re-raise exception

        return False


class _NoopTaskTracker:
    """TaskTracker that does nothing (used when no provider is mounted)."""

    def step(self, message: str) -> None:
        pass

    def set_progress(self, value: float) -> None:
        pass

    def update(self, title: str) -> None:
        pass

    def complete(self, message: Optional[str] = None) -> None:
        pass

    def fail(self, message: str) -> None:
        pass

    def cancel(self) -> None:
        pass


class _NoopTaskTrackerContextManager(_NoopTaskTracker):
    """Noop context manager version."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class NoopNotifier:
    """Notifier that does nothing (used when no provider is mounted)."""

    def success(self, message: str) -> None:
        pass

    def error(self, message: str) -> None:
        pass

    def warning(self, message: str) -> None:
        pass

    def info(self, message: str) -> None:
        pass

    def dismiss(self, toast_id: str) -> None:
        pass

    def track(self, title: str, total_steps: Optional[int] = None):
        return _NoopTaskTrackerContextManager()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_solara/test_notifications/test_notifier.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add pysepal/solara/notifications/notifier.py \
       tests/test_solara/test_notifications/test_notifier.py
git commit -m "feat(notifications): add Notifier publisher and TaskTracker context manager"
```

---

### Task 4: NotificationProvider and use_notifications Hook

**Files:**

- Create: `pysepal/solara/notifications/provider.py`
- Create: `pysepal/solara/notifications/hook.py`
- Create: `tests/test_solara/test_notifications/test_hook.py`

- [ ] **Step 1: Write failing tests for the hook**

File: `tests/test_solara/test_notifications/test_hook.py`

```python
"""Tests for use_notifications hook and bus resolution."""

from unittest.mock import patch

import pytest

from pysepal.solara.notifications.bus import (
    NotificationBus,
    _buses,
    create_bus,
)
from pysepal.solara.notifications.hook import use_notifications_from_bus
from pysepal.solara.notifications.notifier import Notifier, NoopNotifier
from pysepal.solara.notifications.state import ToastType


class TestUseNotificationsFromBus:
    """Test the bus-resolution logic (non-Solara, pure Python)."""

    def test_returns_notifier_with_bus(self):
        bus = NotificationBus()
        notifier = use_notifications_from_bus(bus)
        assert isinstance(notifier, Notifier)

    def test_returns_noop_without_bus(self):
        notifier = use_notifications_from_bus(None)
        assert isinstance(notifier, NoopNotifier)

    def test_notifier_publishes_to_bus(self):
        bus = NotificationBus()
        notifier = use_notifications_from_bus(bus)
        notifier.success("hello")
        assert len(bus.toasts.value) == 1
        assert bus.toasts.value[0].type == ToastType.SUCCESS
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_solara/test_notifications/test_hook.py -v`
Expected: `ModuleNotFoundError: No module named 'pysepal.solara.notifications.hook'`

- [ ] **Step 3: Implement hook module**

File: `pysepal/solara/notifications/hook.py`

```python
"""Solara hook: use_notifications()."""

import logging
from typing import Optional, Union

import solara

from .bus import NotificationBus, get_current_bus
from .notifier import Notifier, NoopNotifier

logger = logging.getLogger(__name__)


def use_notifications_from_bus(
    bus: Optional[NotificationBus],
) -> Union[Notifier, NoopNotifier]:
    """Resolve a Notifier from a bus (testable without Solara context)."""
    if bus is None:
        logger.warning(
            "use_notifications() called without a mounted NotificationProvider. "
            "Notifications will be silently dropped."
        )
        return NoopNotifier()
    return Notifier(bus)


def use_notifications() -> Union[Notifier, NoopNotifier]:
    """Solara hook: returns a Notifier bound to the current kernel's bus.

    Must be called inside a Solara component function.
    If no NotificationProvider is mounted, returns a NoopNotifier.
    """
    bus = get_current_bus()
    return solara.use_memo(lambda: use_notifications_from_bus(bus), [bus])
```

- [ ] **Step 4: Implement provider component**

File: `pysepal/solara/notifications/provider.py`

```python
"""NotificationProvider: root component that creates the kernel-scoped bus."""

import logging

import solara

from .bus import create_bus, cleanup_bus, get_current_bus

logger = logging.getLogger(__name__)


@solara.component
def NotificationProvider(progress_style: str = "pill"):
    """Root notification component. Place once at app top level.

    Creates a kernel-scoped NotificationBus and renders the notification UI
    (ToastStack + TaskProgressPill or TaskProgressStrip).

    Args:
        progress_style: "pill" (default, floating pill) or "strip" (bottom bar, deferred).
    """
    from .task_pill import TaskProgressPill
    from .toast_stack import ToastStack

    # Create bus on first render, cleanup on unmount
    def setup_bus():
        bus = get_current_bus()
        if bus is None:
            bus = create_bus()
            logger.debug("NotificationProvider: created bus")

        def on_cleanup():
            cleanup_bus()
            logger.debug("NotificationProvider: cleaned up bus")

        return on_cleanup

    solara.use_effect(setup_bus, [])

    bus = get_current_bus()
    if bus is None:
        return

    ToastStack(bus=bus)
    if progress_style == "pill":
        TaskProgressPill(bus=bus)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_solara/test_notifications/test_hook.py -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add pysepal/solara/notifications/hook.py \
       pysepal/solara/notifications/provider.py \
       tests/test_solara/test_notifications/test_hook.py
git commit -m "feat(notifications): add NotificationProvider and use_notifications hook"
```

---

### Task 5: ToastStack Component

**Files:**

- Create: `pysepal/solara/notifications/toast_stack.py`
- Create: `tests/test_solara/test_notifications/test_toast_stack.py`

- [ ] **Step 1: Write failing tests for ToastStack rendering logic**

File: `tests/test_solara/test_notifications/test_toast_stack.py`

```python
"""Tests for ToastStack helper logic (non-component, pure Python)."""

from pysepal.solara.notifications.toast_stack import visible_toasts, ERROR_ROTATION_SECONDS
from pysepal.solara.notifications.state import Toast, ToastType
import time


class TestVisibleToasts:
    def test_max_three_visible(self):
        toasts = [Toast(message=f"msg-{i}") for i in range(5)]
        visible = visible_toasts(toasts)
        assert len(visible) == 3

    def test_newest_first(self):
        now = time.time()
        toasts = [
            Toast(message="old", created_at=now - 10),
            Toast(message="mid", created_at=now - 5),
            Toast(message="new", created_at=now),
        ]
        visible = visible_toasts(toasts)
        assert visible[0].message == "new"
        assert visible[2].message == "old"

    def test_errors_rotate_after_timeout(self):
        now = time.time()
        old_errors = [
            Toast(
                message=f"err-{i}",
                type=ToastType.ERROR,
                created_at=now - ERROR_ROTATION_SECONDS - 10,
            )
            for i in range(3)
        ]
        new_info = Toast(message="info", type=ToastType.INFO, created_at=now)
        toasts = old_errors + [new_info]
        visible = visible_toasts(toasts, now=now)
        # Old errors should be rotated out, new info should be visible
        info_visible = [t for t in visible if t.type == ToastType.INFO]
        assert len(info_visible) == 1

    def test_fresh_errors_are_not_rotated(self):
        now = time.time()
        fresh_error = Toast(message="err", type=ToastType.ERROR, created_at=now - 5)
        toasts = [fresh_error]
        visible = visible_toasts(toasts, now=now)
        assert len(visible) == 1
        assert visible[0].type == ToastType.ERROR
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_solara/test_notifications/test_toast_stack.py -v`
Expected: `ModuleNotFoundError: No module named 'pysepal.solara.notifications.toast_stack'`

- [ ] **Step 3: Implement ToastStack**

File: `pysepal/solara/notifications/toast_stack.py`

```python
"""ToastStack: floating toast notification renderer."""

import time
from typing import Optional

import reacton.ipyvuetify as rv
import solara

from .bus import NotificationBus
from .state import Toast, ToastType, TOAST_TIMEOUT_DEFAULTS

MAX_VISIBLE = 3
ERROR_ROTATION_SECONDS = 30.0

# Color mapping for toast types
TOAST_COLORS = {
    ToastType.SUCCESS: "success",
    ToastType.INFO: "info",
    ToastType.WARNING: "warning",
    ToastType.ERROR: "error",
}


def visible_toasts(
    toasts: list[Toast],
    now: Optional[float] = None,
) -> list[Toast]:
    """Determine which toasts to display (max 3, newest first, error rotation)."""
    if now is None:
        now = time.time()

    # Separate stale errors (older than rotation threshold) from fresh toasts
    stale_errors = []
    fresh = []
    for t in toasts:
        if (
            t.type == ToastType.ERROR
            and (now - t.created_at) > ERROR_ROTATION_SECONDS
        ):
            stale_errors.append(t)
        else:
            fresh.append(t)

    # Sort fresh by newest first
    fresh.sort(key=lambda t: t.created_at, reverse=True)

    # Take up to MAX_VISIBLE from fresh toasts
    visible = fresh[:MAX_VISIBLE]

    # If there's room and stale errors exist, add them
    remaining_slots = MAX_VISIBLE - len(visible)
    if remaining_slots > 0 and stale_errors:
        stale_errors.sort(key=lambda t: t.created_at, reverse=True)
        visible.extend(stale_errors[:remaining_slots])

    return visible[:MAX_VISIBLE]


@solara.component
def ToastCard(toast: Toast, on_dismiss: callable):
    """A single toast notification card."""
    color = TOAST_COLORS.get(toast.type, "info")
    timeout = toast.effective_timeout()

    # Auto-dismiss timer
    if timeout is not None:
        timeout_ms = int(timeout * 1000)
    else:
        timeout_ms = -1  # Vuetify: -1 means no auto-dismiss

    count_text = f" (x{toast.count})" if toast.count > 1 else ""

    rv.Snackbar(
        v_model=True,
        color=color,
        timeout=timeout_ms,
        top=True,
        right=True,
        children=[
            solara.Text(f"{toast.message}{count_text}"),
            rv.Btn(
                icon=True,
                children=[rv.Icon(children=["mdi-close"])],
                on_click=lambda *_: on_dismiss(toast.id),
                class_="ml-2",
                small=True,
            ),
        ],
        style_="position: relative; margin-bottom: 8px;",
        on_v_model=lambda v: on_dismiss(toast.id) if not v else None,
    )


@solara.component
def ToastStack(bus: NotificationBus):
    """Renders stacked toast notifications, floating top-right."""
    toasts = bus.toasts.value
    visible = visible_toasts(toasts)

    def dismiss(toast_id):
        bus.remove_toast(toast_id)

    with solara.Column(
        style={
            "position": "fixed",
            "top": "16px",
            "right": "16px",
            "z-index": "1000",
            "width": "350px",
            "pointer-events": "none",
            "display": "flex",
            "flex-direction": "column",
            "gap": "8px",
        },
    ):
        for toast in visible:
            with solara.Div(style={"pointer-events": "auto"}):
                ToastCard(toast=toast, on_dismiss=dismiss)

        # Show rotated error count if any
        stale_error_count = len(toasts) - len(visible)
        if stale_error_count > 0:
            error_count = len(
                [t for t in toasts if t.type == ToastType.ERROR and t not in visible]
            )
            if error_count > 0:
                with solara.Div(style={"pointer-events": "auto"}):
                    rv.Chip(
                        color="error",
                        small=True,
                        children=[f"{error_count} more error(s)"],
                        on_click=lambda *_: None,  # TODO: expand errors
                    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_solara/test_notifications/test_toast_stack.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add pysepal/solara/notifications/toast_stack.py \
       tests/test_solara/test_notifications/test_toast_stack.py
git commit -m "feat(notifications): add ToastStack component with auto-dismiss and error rotation"
```

---

### Task 6: TaskProgressPill Component

**Files:**

- Create: `pysepal/solara/notifications/task_pill.py`
- Create: `tests/test_solara/test_notifications/test_task_pill.py`

- [ ] **Step 1: Write failing tests for TaskProgressPill helper logic**

File: `tests/test_solara/test_notifications/test_task_pill.py`

```python
"""Tests for TaskProgressPill helper logic (non-component, pure Python)."""

from pysepal.solara.notifications.task_pill import (
    active_task_count,
    task_summary_text,
)
from pysepal.solara.notifications.state import (
    TrackedTask,
    TaskStatus,
    TaskMilestone,
)


class TestActiveTaskCount:
    def test_counts_running_and_pending(self):
        tasks = [
            TrackedTask(title="a", status=TaskStatus.RUNNING),
            TrackedTask(title="b", status=TaskStatus.PENDING),
            TrackedTask(title="c", status=TaskStatus.COMPLETED),
            TrackedTask(title="d", status=TaskStatus.FAILED),
        ]
        assert active_task_count(tasks) == 2

    def test_zero_when_none_active(self):
        tasks = [
            TrackedTask(title="a", status=TaskStatus.COMPLETED),
            TrackedTask(title="b", status=TaskStatus.CANCELLED),
        ]
        assert active_task_count(tasks) == 0

    def test_zero_for_empty_list(self):
        assert active_task_count([]) == 0


class TestTaskSummaryText:
    def test_single_task(self):
        assert task_summary_text(1) == "1 task running"

    def test_multiple_tasks(self):
        assert task_summary_text(3) == "3 tasks running"

    def test_zero_tasks(self):
        assert task_summary_text(0) == ""
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_solara/test_notifications/test_task_pill.py -v`
Expected: `ModuleNotFoundError: No module named 'pysepal.solara.notifications.task_pill'`

- [ ] **Step 3: Implement TaskProgressPill**

File: `pysepal/solara/notifications/task_pill.py`

```python
"""TaskProgressPill: floating task progress indicator with expandable detail."""

from typing import Optional

import reacton.ipyvuetify as rv
import solara

from .bus import NotificationBus
from .state import TrackedTask, TaskStatus, TaskMilestone

ACTIVE_STATUSES = {TaskStatus.RUNNING, TaskStatus.PENDING}
COMPLETED_FADE_SECONDS = 3.0

# Status colors
STATUS_COLORS = {
    TaskStatus.RUNNING: "primary",
    TaskStatus.PENDING: "grey",
    TaskStatus.COMPLETED: "success",
    TaskStatus.FAILED: "error",
    TaskStatus.CANCELLED: "grey",
}


def active_task_count(tasks: list[TrackedTask]) -> int:
    """Count tasks that are still running or pending."""
    return sum(1 for t in tasks if t.status in ACTIVE_STATUSES)


def task_summary_text(count: int) -> str:
    """Generate summary text for the pill badge."""
    if count == 0:
        return ""
    if count == 1:
        return "1 task running"
    return f"{count} tasks running"


@solara.component
def MilestoneTimeline(milestones: tuple[TaskMilestone, ...]):
    """Render a task's milestone history as a timeline."""
    with rv.Timeline(dense=True, align_top=True):
        for ms in milestones:
            with rv.TimelineItem(small=True, color="primary"):
                solara.Text(ms.message)


@solara.component
def TaskCard(task: TrackedTask):
    """A single task entry in the expanded detail panel."""
    color = STATUS_COLORS.get(task.status, "grey")
    expanded, set_expanded = solara.use_state(False)

    with rv.Card(outlined=True, class_="mb-2"):
        with rv.CardTitle(class_="py-2"):
            with solara.Row(justify="space-between", style={"width": "100%"}):
                solara.Text(task.title)
                rv.Chip(
                    x_small=True,
                    color=color,
                    children=[task.status.value],
                )

        # Current step / progress
        with rv.CardText(class_="py-1"):
            if task.milestones:
                last_ms = task.milestones[-1]
                solara.Text(last_ms.message, style={"font-size": "0.85em"})

            if task.progress is not None:
                rv.ProgressLinear(
                    value=int(task.progress * 100),
                    color=color,
                    height=6,
                    rounded=True,
                    class_="mt-1",
                )

            if task.total_steps and task.current_step:
                solara.Text(
                    f"Step {task.current_step}/{task.total_steps}",
                    style={"font-size": "0.75em", "color": "grey"},
                )

            if task.error_message:
                solara.Text(
                    task.error_message,
                    style={"color": "red", "font-size": "0.85em"},
                )

        # Expandable milestone timeline
        if task.milestones:
            with rv.CardActions(class_="py-0"):
                rv.Btn(
                    text=True,
                    x_small=True,
                    children=["Show steps" if not expanded else "Hide steps"],
                    on_click=lambda *_: set_expanded(not expanded),
                )

            if expanded:
                with rv.CardText(class_="pt-0"):
                    MilestoneTimeline(milestones=task.milestones)


@solara.component
def TaskProgressPill(bus: NotificationBus):
    """Floating pill showing active task count, expandable to detail panel."""
    tasks = bus.tasks.value
    count = active_task_count(tasks)
    expanded, set_expanded = solara.use_state(False)

    # Filter out tasks to display (active + recently finished)
    display_tasks = [
        t
        for t in tasks
        if t.status in ACTIVE_STATUSES
        or t.status in {TaskStatus.FAILED, TaskStatus.CANCELLED}
    ]

    # Nothing to show
    if not display_tasks and count == 0:
        return

    summary = task_summary_text(count)

    with solara.Div(
        style={
            "position": "fixed",
            "bottom": "16px",
            "left": "16px",
            "z-index": "1000",
            "pointer-events": "auto",
        },
    ):
        if not expanded:
            # Collapsed pill
            rv.Btn(
                rounded=True,
                color="primary",
                dark=True,
                small=True,
                children=[
                    rv.ProgressCircular(
                        indeterminate=True,
                        size=16,
                        width=2,
                        class_="mr-2",
                    )
                    if count > 0
                    else None,
                    summary or f"{len(display_tasks)} task(s)",
                ],
                on_click=lambda *_: set_expanded(True),
            )
        else:
            # Expanded detail panel
            with rv.Card(
                max_width=400,
                min_width=300,
                style_="max-height: 400px; overflow-y: auto;",
            ):
                with rv.CardTitle(class_="py-2"):
                    with solara.Row(
                        justify="space-between", style={"width": "100%"}
                    ):
                        solara.Text("Task Progress")
                        rv.Btn(
                            icon=True,
                            small=True,
                            children=[rv.Icon(children=["mdi-close"])],
                            on_click=lambda *_: set_expanded(False),
                        )
                with rv.CardText():
                    if not display_tasks:
                        solara.Text("No active tasks")
                    else:
                        for task in display_tasks:
                            TaskCard(task=task)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_solara/test_notifications/test_task_pill.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add pysepal/solara/notifications/task_pill.py \
       tests/test_solara/test_notifications/test_task_pill.py
git commit -m "feat(notifications): add TaskProgressPill component with milestone timeline"
```

---

### Task 7: Global Functions (notify, track_task)

**Files:**

- Create: `pysepal/solara/notifications/globals.py`
- Create: `tests/test_solara/test_notifications/test_globals.py`

- [ ] **Step 1: Write failing tests for global functions**

File: `tests/test_solara/test_notifications/test_globals.py`

```python
"""Tests for global notify() and track_task() functions."""

import logging
from unittest.mock import patch

import pytest

from pysepal.solara.notifications.bus import NotificationBus, _buses
from pysepal.solara.notifications.state import ToastType, TaskStatus


class TestNotify:
    def setup_method(self):
        _buses.clear()

    def teardown_method(self):
        _buses.clear()

    @patch("pysepal.solara.notifications.globals._get_kernel_id", return_value="k1")
    @patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="k1")
    def test_notify_publishes_toast(self, mock_bus_kid, mock_globals_kid):
        from pysepal.solara.notifications.bus import create_bus
        from pysepal.solara.notifications.globals import notify

        bus = create_bus()
        notify("hello", type="success")
        assert len(bus.toasts.value) == 1
        assert bus.toasts.value[0].message == "hello"
        assert bus.toasts.value[0].type == ToastType.SUCCESS

    @patch("pysepal.solara.notifications.globals._get_kernel_id", return_value="k1")
    @patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="k1")
    def test_notify_default_type_is_info(self, mock_bus_kid, mock_globals_kid):
        from pysepal.solara.notifications.bus import create_bus
        from pysepal.solara.notifications.globals import notify

        create_bus()
        notify("hello")
        assert _buses["k1"].toasts.value[0].type == ToastType.INFO

    def test_notify_without_provider_logs_warning(self, caplog):
        from pysepal.solara.notifications.globals import notify

        with caplog.at_level(logging.WARNING):
            notify("hello", type="error")
        assert "NotificationProvider" in caplog.text

    @patch("pysepal.solara.notifications.globals._get_kernel_id", return_value="k1")
    @patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="k1")
    def test_track_task_context_manager(self, mock_bus_kid, mock_globals_kid):
        from pysepal.solara.notifications.bus import create_bus
        from pysepal.solara.notifications.globals import track_task

        bus = create_bus()
        with track_task("Processing", total_steps=2) as task:
            task.step("Step 1")
            task.set_progress(0.5)
        assert len(bus.tasks.value) == 1
        assert bus.tasks.value[0].status == TaskStatus.COMPLETED

    def test_track_task_without_provider_is_noop(self):
        from pysepal.solara.notifications.globals import track_task

        # Should not raise
        with track_task("Processing") as task:
            task.step("Step 1")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_solara/test_notifications/test_globals.py -v`
Expected: `ModuleNotFoundError: No module named 'pysepal.solara.notifications.globals'`

- [ ] **Step 3: Implement global functions**

File: `pysepal/solara/notifications/globals.py`

```python
"""Global escape-hatch functions: notify() and track_task()."""

import logging
from typing import Optional

from .bus import get_current_bus
from .notifier import Notifier, NoopNotifier, _NoopTaskTrackerContextManager
from .state import Toast, ToastType

logger = logging.getLogger(__name__)

_TYPE_MAP = {
    "success": ToastType.SUCCESS,
    "info": ToastType.INFO,
    "warning": ToastType.WARNING,
    "error": ToastType.ERROR,
}


def _get_kernel_id() -> Optional[str]:
    """Get kernel ID, returning None if not in Solara context."""
    try:
        import solara.server.kernel_context

        return str(
            id(solara.server.kernel_context.get_current_context().kernel)
        )
    except Exception:
        return None


def notify(message: str, type: str = "info") -> None:
    """Publish a toast notification from anywhere (non-component code).

    If no NotificationProvider is mounted, logs a warning and drops the message.

    Args:
        message: The notification text.
        type: One of "success", "info", "warning", "error".
    """
    bus = get_current_bus()
    if bus is None:
        logger.warning(
            "notify() called without a mounted NotificationProvider. "
            f"Dropped: {type}={message!r}"
        )
        return

    toast_type = _TYPE_MAP.get(type, ToastType.INFO)
    bus.add_toast(Toast(message=message, type=toast_type))


def track_task(title: str, total_steps: Optional[int] = None):
    """Return a TaskTracker context manager from anywhere (non-component code).

    If no NotificationProvider is mounted, returns a no-op context manager.

    Args:
        title: Task title displayed in the progress panel.
        total_steps: If known, enables "step N/M" display.
    """
    bus = get_current_bus()
    if bus is None:
        logger.warning(
            "track_task() called without a mounted NotificationProvider. "
            f"Dropped: {title!r}"
        )
        return _NoopTaskTrackerContextManager()

    notifier = Notifier(bus)
    return notifier.track(title, total_steps=total_steps)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_solara/test_notifications/test_globals.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add pysepal/solara/notifications/globals.py \
       tests/test_solara/test_notifications/test_globals.py
git commit -m "feat(notifications): add notify() and track_task() global functions"
```

---

### Task 8: Adapt @catch_errors Decorator

**Files:**

- Modify: `pysepal/scripts/decorator.py:25-87`
- Create: `tests/test_solara/test_notifications/test_catch_errors.py`

- [ ] **Step 1: Write failing tests for adapted @catch_errors**

File: `tests/test_solara/test_notifications/test_catch_errors.py`

```python
"""Tests for @catch_errors notification bus integration."""

import warnings
from unittest.mock import patch

import pytest

from pysepal.solara.notifications.bus import NotificationBus, _buses
from pysepal.solara.notifications.state import ToastType
from pysepal.scripts.decorator import catch_errors
from pysepal.scripts.warning import SepalWarning


class FakeWidget:
    """Minimal stand-in that mimics the old Alert interface for legacy test."""

    def __init__(self):
        self.messages = []

    def reset(self):
        pass

    def add_msg(self, msg, type_="info"):
        self.messages.append((msg, type_))

    def append_msg(self, msg, type_="info"):
        self.messages.append((msg, type_))


class TestCatchErrorsWithBus:
    def setup_method(self):
        _buses.clear()

    def teardown_method(self):
        _buses.clear()

    @patch("pysepal.scripts.decorator._get_notification_bus")
    def test_exception_publishes_error_toast(self, mock_get_bus):
        bus = NotificationBus()
        mock_get_bus.return_value = bus

        class MyClass:
            @catch_errors
            def do_work(self):
                raise ValueError("boom")

        obj = MyClass()
        with pytest.raises(ValueError, match="boom"):
            obj.do_work()

        assert len(bus.toasts.value) == 1
        assert bus.toasts.value[0].type == ToastType.ERROR
        assert bus.toasts.value[0].message == "boom"

    @patch("pysepal.scripts.decorator._get_notification_bus")
    def test_exception_is_reraised(self, mock_get_bus):
        bus = NotificationBus()
        mock_get_bus.return_value = bus

        class MyClass:
            @catch_errors
            def do_work(self):
                raise RuntimeError("fail")

        obj = MyClass()
        with pytest.raises(RuntimeError, match="fail"):
            obj.do_work()

    @patch("pysepal.scripts.decorator._get_notification_bus")
    def test_sepal_warning_publishes_warning_toast(self, mock_get_bus):
        bus = NotificationBus()
        mock_get_bus.return_value = bus

        class MyClass:
            @catch_errors
            def do_work(self):
                warnings.warn(SepalWarning("careful"))
                return "ok"

        obj = MyClass()
        result = obj.do_work()
        assert result == "ok"
        assert len(bus.toasts.value) == 1
        assert bus.toasts.value[0].type == ToastType.WARNING

    @patch("pysepal.scripts.decorator._get_notification_bus")
    def test_return_value_passed_through(self, mock_get_bus):
        mock_get_bus.return_value = NotificationBus()

        class MyClass:
            @catch_errors
            def do_work(self):
                return 42

        assert MyClass().do_work() == 42

    def test_legacy_alert_param_still_works(self):
        """Passing alert= uses old behavior."""
        alert = FakeWidget()

        class MyClass:
            @catch_errors(alert=alert)
            def do_work(self):
                raise ValueError("old style")

        with pytest.raises(ValueError):
            MyClass().do_work()
        assert ("old style", "error") in alert.messages
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_solara/test_notifications/test_catch_errors.py -v`
Expected: FAIL — `_get_notification_bus` not found in decorator module

- [ ] **Step 3: Modify @catch_errors to support notification bus**

Edit `pysepal/scripts/decorator.py`. The key changes are:

1. Add a `_get_notification_bus()` helper that calls `get_current_bus()` safely
2. When `alert=` is not provided AND no `self.alert` exists, fall back to the notification bus
3. Preserve the original behavior when `alert=` is provided or `self.alert` exists

Add at the top of the file (after existing imports):

```python
import logging

_decorator_logger = logging.getLogger(__name__)


def _get_notification_bus():
    """Try to get the current notification bus. Returns None if unavailable."""
    try:
        from pysepal.solara.notifications.bus import get_current_bus

        return get_current_bus()
    except ImportError:
        return None
```

Then modify the `catch_errors` function to handle three cases:

1. Explicit `alert=` parameter → use old behavior
2. `self.alert` exists → use old behavior
3. Neither → try notification bus, fall back to no-op

Replace the `wrapper_alert_error` function body:

```python
def wrapper_alert_error(self, *args, **kwargs):
    # Resolve alert: explicit param > self.alert > notification bus
    alert_ = alert if alert else getattr(self, "alert", None)

    # If we have a legacy alert widget, use old behavior
    if alert_ is not None:
        alert_.reset()
        value = None
        try:
            with warnings.catch_warnings(record=True) as w_list:
                value = func(self, *args, **kwargs)
            if w_list:
                w_list_sepal = [
                    w for w in w_list if isinstance(w.message, SepalWarning)
                ]
                ms_list = [
                    f"{w.category.__name__}: {w.message.args[0]}"
                    for w in w_list_sepal
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

            w_list_sepal = [
                w for w in w_list if isinstance(w.message, SepalWarning)
            ]
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
```

Also update the `catch_errors` signature to allow calling without parentheses:

```python
def catch_errors(func=None, alert=None, debug=None):
    if debug is not None:
        warn("debug argument defaults to `True`. It will be removed in v3.2")

    def decorator_alert_error(func):
        @wraps(func)
        def wrapper_alert_error(self, *args, **kwargs):
            # ... (body from above)
        return wrapper_alert_error

    # Support both @catch_errors and @catch_errors(alert=...)
    if func is not None:
        return decorator_alert_error(func)
    return decorator_alert_error
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_solara/test_notifications/test_catch_errors.py -v`
Expected: All tests PASS

- [ ] **Step 5: Run existing decorator tests to verify no regression**

Run: `python -m pytest tests/test_scripts/test_decorator.py -v`
Expected: All existing tests PASS (legacy behavior preserved)

- [ ] **Step 6: Commit**

```bash
git add pysepal/scripts/decorator.py \
       tests/test_solara/test_notifications/test_catch_errors.py
git commit -m "feat(notifications): adapt @catch_errors to publish to notification bus"
```

---

### Task 9: Package Init and Integration Wiring

**Files:**

- Modify: `pysepal/solara/notifications/__init__.py`
- Modify: `pysepal/solara/__init__.py`

- [ ] **Step 1: Update notifications package init with public exports**

File: `pysepal/solara/notifications/__init__.py`

```python
"""Centralized notification system for pysepal Solara applications.

Usage::

    from pysepal.solara.notifications import (
        NotificationProvider,  # Place once at app root
        use_notifications,     # Hook for Solara components
        notify,                # Global function for non-component code
        track_task,            # Global task tracking for non-component code
    )
"""

from .globals import notify, track_task
from .hook import use_notifications
from .provider import NotificationProvider
from .state import (
    TOAST_TIMEOUT_DEFAULTS,
    TaskMilestone,
    TaskStatus,
    Toast,
    ToastType,
    TrackedTask,
)
from .toast_stack import ToastStack
from .task_pill import TaskProgressPill

__all__ = [
    "NotificationProvider",
    "TaskProgressPill",
    "ToastStack",
    "notify",
    "track_task",
    "use_notifications",
    "Toast",
    "ToastType",
    "TaskMilestone",
    "TaskStatus",
    "TrackedTask",
    "TOAST_TIMEOUT_DEFAULTS",
]
```

- [ ] **Step 2: Update solara package init to expose notifications**

Add to `pysepal/solara/__init__.py`:

```python
from .notifications import (
    NotificationProvider,
    notify,
    track_task,
    use_notifications,
)
```

And add to `__all__`:

```python
__all__ = [
    # ... existing exports ...
    "NotificationProvider",
    "notify",
    "track_task",
    "use_notifications",
]
```

- [ ] **Step 3: Verify imports work**

Run:

```bash
python -c "
from pysepal.solara.notifications import (
    NotificationProvider, use_notifications, notify, track_task,
    Toast, ToastType, TaskStatus, TrackedTask, TaskMilestone,
    ToastStack, TaskProgressPill, TOAST_TIMEOUT_DEFAULTS,
)
print('All notification imports OK')

from pysepal.solara import (
    NotificationProvider, use_notifications, notify, track_task,
)
print('All solara-level imports OK')
"
```

Expected: Both print statements succeed

- [ ] **Step 4: Run full test suite**

Run: `python -m pytest tests/test_solara/ -v`
Expected: All notification tests PASS

- [ ] **Step 5: Commit**

```bash
git add pysepal/solara/notifications/__init__.py pysepal/solara/__init__.py
git commit -m "feat(notifications): wire up package exports and public API"
```

---

### Task 10: Integration Smoke Test

**Files:**

- Create: `tests/test_solara/test_notifications/test_integration.py`

- [ ] **Step 1: Write integration test**

File: `tests/test_solara/test_notifications/test_integration.py`

```python
"""Integration test: full notification flow without Solara server."""

from unittest.mock import patch

import pytest

from pysepal.solara.notifications.bus import (
    NotificationBus,
    _buses,
    create_bus,
)
from pysepal.solara.notifications.notifier import Notifier
from pysepal.solara.notifications.state import (
    TaskStatus,
    ToastType,
)


class TestFullNotificationFlow:
    """End-to-end: create bus, publish, track, verify state."""

    def setup_method(self):
        _buses.clear()

    def teardown_method(self):
        _buses.clear()

    @patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="test-kernel")
    def test_toast_and_task_flow(self, mock_kid):
        bus = create_bus()
        notifier = Notifier(bus)

        # Publish toasts
        notifier.success("Upload complete")
        notifier.warning("Large file detected")
        notifier.error("Connection timeout")

        assert len(bus.toasts.value) == 3
        assert bus.toasts.value[0].type == ToastType.SUCCESS
        assert bus.toasts.value[1].type == ToastType.WARNING
        assert bus.toasts.value[2].type == ToastType.ERROR

        # Track a task with milestones
        with notifier.track("Processing AOI", total_steps=3) as task:
            task.step("Validating geometry...")
            assert bus.tasks.value[0].current_step == 1
            assert bus.tasks.value[0].status == TaskStatus.RUNNING

            task.step("Fetching from GEE...")
            task.set_progress(0.5)
            assert bus.tasks.value[0].current_step == 2
            assert bus.tasks.value[0].progress == 0.5

            task.step("Clipping raster...")
            task.set_progress(0.9)

        # Task completed
        assert bus.tasks.value[0].status == TaskStatus.COMPLETED
        assert bus.tasks.value[0].progress == 1.0
        assert len(bus.tasks.value[0].milestones) == 3

        # Dismiss a toast
        toast_id = bus.toasts.value[0].id
        notifier.dismiss(toast_id)
        assert len(bus.toasts.value) == 2

    @patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="test-kernel")
    def test_task_failure_flow(self, mock_kid):
        bus = create_bus()
        notifier = Notifier(bus)

        with pytest.raises(RuntimeError, match="GEE timeout"):
            with notifier.track("Export") as task:
                task.step("Preparing data...")
                task.set_progress(0.3)
                raise RuntimeError("GEE timeout")

        t = bus.tasks.value[0]
        assert t.status == TaskStatus.FAILED
        assert t.error_message == "GEE timeout"
        assert len(t.milestones) == 1
        assert t.milestones[0].message == "Preparing data..."

        # Error toast auto-published
        assert len(bus.toasts.value) == 1
        assert bus.toasts.value[0].type == ToastType.ERROR
        assert "GEE timeout" in bus.toasts.value[0].message

    @patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="test-kernel")
    def test_concurrent_tasks(self, mock_kid):
        bus = create_bus()
        notifier = Notifier(bus)

        tracker1 = notifier.track("Task A", total_steps=2)
        tracker2 = notifier.track("Task B")

        with tracker1 as t1:
            t1.step("A step 1")
            with tracker2 as t2:
                t2.step("B step 1")
                t2.set_progress(0.5)
            # tracker2 auto-completed
            t1.step("A step 2")

        assert len(bus.tasks.value) == 2
        assert bus.tasks.value[0].status == TaskStatus.COMPLETED
        assert bus.tasks.value[1].status == TaskStatus.COMPLETED

    @patch("pysepal.solara.notifications.bus._get_kernel_id", return_value="test-kernel")
    def test_dedup_toasts(self, mock_kid):
        bus = create_bus()
        notifier = Notifier(bus)

        # Rapid-fire identical toasts
        for _ in range(5):
            notifier.info("Loading...")

        # Should be deduped to one toast with count=5
        assert len(bus.toasts.value) == 1
        assert bus.toasts.value[0].count == 5
```

- [ ] **Step 2: Run integration tests**

Run: `python -m pytest tests/test_solara/test_notifications/test_integration.py -v`
Expected: All tests PASS

- [ ] **Step 3: Run full notification test suite**

Run: `python -m pytest tests/test_solara/ -v --tb=short`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add tests/test_solara/test_notifications/test_integration.py
git commit -m "test(notifications): add integration tests for full notification flow"
```

---

## File Summary

| File                                                        | Action | Responsibility                                                        |
| ----------------------------------------------------------- | ------ | --------------------------------------------------------------------- |
| `pysepal/solara/notifications/__init__.py`                  | Create | Public API exports                                                    |
| `pysepal/solara/notifications/state.py`                     | Create | Dataclasses, enums, timeout defaults                                  |
| `pysepal/solara/notifications/bus.py`                       | Create | NotificationBus, kernel registry, thread-safe mutations               |
| `pysepal/solara/notifications/notifier.py`                  | Create | Notifier (toast methods), TaskTracker (context manager), NoopNotifier |
| `pysepal/solara/notifications/hook.py`                      | Create | `use_notifications()` Solara hook                                     |
| `pysepal/solara/notifications/provider.py`                  | Create | `NotificationProvider` root component                                 |
| `pysepal/solara/notifications/toast_stack.py`               | Create | `ToastStack` floating toast renderer                                  |
| `pysepal/solara/notifications/task_pill.py`                 | Create | `TaskProgressPill` floating progress indicator                        |
| `pysepal/solara/notifications/globals.py`                   | Create | `notify()`, `track_task()` global functions                           |
| `pysepal/scripts/decorator.py`                              | Modify | Adapt `@catch_errors` for notification bus                            |
| `pysepal/solara/__init__.py`                                | Modify | Add notification exports                                              |
| `tests/test_solara/__init__.py`                             | Create | Test package                                                          |
| `tests/test_solara/test_notifications/__init__.py`          | Create | Test subpackage                                                       |
| `tests/test_solara/test_notifications/test_state.py`        | Create | State model tests                                                     |
| `tests/test_solara/test_notifications/test_bus.py`          | Create | Bus mutation + registry tests                                         |
| `tests/test_solara/test_notifications/test_notifier.py`     | Create | Notifier + TaskTracker tests                                          |
| `tests/test_solara/test_notifications/test_hook.py`         | Create | Hook resolution tests                                                 |
| `tests/test_solara/test_notifications/test_toast_stack.py`  | Create | Toast visibility logic tests                                          |
| `tests/test_solara/test_notifications/test_task_pill.py`    | Create | Pill helper logic tests                                               |
| `tests/test_solara/test_notifications/test_globals.py`      | Create | Global function tests                                                 |
| `tests/test_solara/test_notifications/test_catch_errors.py` | Create | Adapted decorator tests                                               |
| `tests/test_solara/test_notifications/test_integration.py`  | Create | End-to-end flow tests                                                 |
