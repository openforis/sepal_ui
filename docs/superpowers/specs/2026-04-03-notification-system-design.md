# Notification System Design

## Overview

A two-layer notification system for pysepal Solara apps that replaces the legacy per-component Alert/Banner/StateBar widgets with a centralized, reactive notification architecture.

**Goals:**

- Remove notification UI from individual components (no more `self.alert = Alert()`)
- Centralized state bus — any component can publish, one place renders
- Two distinct UX layers: ephemeral toasts + persistent task progress
- Pure Solara — no legacy ipyvuetify fallback

## Architecture

```
┌─────────────────── NotificationState (solara.reactive) ───────────────────┐
│  toasts: list[Toast]          tasks: list[TrackedTask]                     │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Publishers:                     Renderers:                                │
│  ├─ use_notifications() hook     ├─ ToastStack (floating, top-right)       │
│  ├─ notify() global function     ├─ TaskProgressPill (floating, bottom-left)│
│  └─ @catch_errors decorator      └─ TaskProgressStrip (bottom bar)         │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Layer 1: Toasts

Ephemeral floating notifications for "something happened" feedback.

**Behavior:**

- Floating top-right of the right side panel
- Stacked, up to 3 visible at a time. Older queued, appear as others dismiss.
- Newest on top
- Colored left border by type
- Close button on each toast
- Slide-in from right, fade-out on dismiss

**Auto-dismiss timing (type-based):**

- `success` / `info`: 5 seconds
- `warning`: 10 seconds
- `error`: persist until manually dismissed

## Layer 2: Task Progress

Persistent indicator for "something is happening" with structured step tracking.

Two renderer variants to compare (share same state):

### TaskProgressPill (Option A)

- Small floating pill at bottom-left
- Collapsed: spinner icon + "N tasks running"
- Click to expand: mini-panel with task details
- Disappears when no tasks active

### TaskProgressStrip (Option B)

- Thin bar fixed at bottom of app
- Compact summary: "Processing AOI (step 2/3) | Exporting..."
- Click to expand same detail panel
- Shows "Ready" or hides when idle

### Expanded Detail Panel (shared by both)

- Each task shows: title, current step message, progress bar (if progress provided)
- Click a task to see full step timeline
- Failed tasks: red, show error message + step history preserved
- Completed tasks: brief "done" flash, fade out after 3 seconds

## State Model

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time
import uuid


class ToastType(Enum):
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class TaskStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class Toast:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message: str = ""
    type: ToastType = ToastType.INFO
    created_at: float = field(default_factory=time.time)
    timeout: Optional[float] = None  # Defaults: SUCCESS/INFO=5.0, WARNING=10.0, ERROR=None


@dataclass(frozen=True)
class TaskStep:
    message: str = ""
    progress: Optional[float] = None  # 0.0 - 1.0
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class TrackedTask:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    status: TaskStatus = TaskStatus.RUNNING
    steps: tuple[TaskStep, ...] = ()  # Immutable for reactive updates
    created_at: float = field(default_factory=time.time)
    error_message: Optional[str] = None


class NotificationState:
    toasts = solara.reactive([])   # list[Toast]
    tasks = solara.reactive([])    # list[TrackedTask]
```

All dataclasses are `frozen=True` to enforce immutable updates required by Solara reactivity.

## Publisher API

### Primary: `use_notifications()` hook

For use inside Solara components:

```python
@solara.component
def AoiView():
    notifications = use_notifications()

    async def process_aoi():
        with notifications.track("Processing AOI") as task:
            task.step("Validating geometry...")
            result = await gee_interface.get_info_async(obj)
            task.step("Fetching from GEE...", progress=0.3)
            data = await gee_interface.get_asset_async(asset_id)
            task.step("Clipping raster...", progress=0.7)
        notifications.success("Assets loaded!")

    solara.lab.use_task(process_aoi, prefer_threaded=False, dependencies=None)
```

**`use_notifications()` returns a `Notifier` with:**

- `.success(msg)`, `.error(msg)`, `.warning(msg)`, `.info(msg)` — publish toasts
- `.track(title) -> TaskTracker` — context manager for task progress
- `.dismiss(toast_id)` — manually dismiss a toast

**`TaskTracker` context manager:**

- `.step(msg, progress=None)` — add step to timeline
- `.update(msg)` — update task title
- `.complete(msg=None)` — explicit completion (also auto-completes on `__exit__`)
- `.fail(msg)` — explicit failure (also auto-fails on exception)

**Failure behavior:** On unhandled exception inside `with notifications.track(...)`:

- Task marked FAILED with step history preserved in tracker
- Error toast auto-published to grab attention
- User can inspect step details in expanded tracker panel

### Escape hatch: `notify()` global function

For non-component code (decorators, scripts, background threads):

```python
from pysepal.solara.notifications import notify

notify("Export failed", type="error")
notify("File saved", type="success")
```

### Adapted `@catch_errors` decorator

```python
@catch_errors  # No alert= param needed
def simple_process(self):
    do_something()
    # Exception → error toast
    # Warnings → warning toast(s)
```

## Integration

### App Root Setup

Place `NotificationProvider` once at the app root:

```python
from pysepal.solara.notifications import NotificationProvider

@solara.component
def Page():
    with MapApp(...):
        NotificationProvider(progress_style="pill")  # or "strip"
        AoiView()
        ExportTile()
```

### Thread Safety

`notify()` global function can be called from background threads. State mutations go through a thread-safe helper that schedules reactive updates on the Solara event loop.

### Cleanup

When `NotificationProvider` unmounts (page navigation): all pending toasts cleared, running tasks cleared.

## File Structure

```
pysepal/solara/notifications/
├── __init__.py          # Public exports
├── state.py             # NotificationState, dataclasses, enums, thread-safe helpers
├── hook.py              # use_notifications(), Notifier, TaskTracker
├── provider.py          # NotificationProvider component
├── toast_stack.py       # ToastStack component
├── task_pill.py         # TaskProgressPill component
├── task_strip.py        # TaskProgressStrip component
└── globals.py           # notify() global function, catch_errors adapter

tests/test_solara/test_notifications/
├── test_state.py        # State mutations, immutability, thread safety
├── test_hook.py         # Hook, track context manager, cleanup
├── test_toast_stack.py  # Rendering, auto-dismiss, max 3 stacking
├── test_task_pill.py    # Collapse/expand, step timeline, failure state
├── test_task_strip.py   # Compact view, expand, idle state
└── test_globals.py      # notify(), catch_errors adapter
```

## Decisions Log

| Decision             | Choice                            | Rationale                                                        |
| -------------------- | --------------------------------- | ---------------------------------------------------------------- |
| Architecture         | Two components, one bus           | Clean UX separation: toasts (ephemeral) vs progress (persistent) |
| Toast position       | Floating top-right of right panel | Where user operations happen                                     |
| Progress position    | Floating bottom-left              | Left panel underused, avoids clutter                             |
| Progress renderers   | Build both pill + strip           | Compare and decide visually                                      |
| API style            | Hook + global escape hatch        | Solara-native, with coverage for non-component code              |
| Auto-dismiss         | Type-based                        | Errors persist (critical), success fades (non-blocking)          |
| Progress granularity | Structured steps with timeline    | Users need visibility into multi-step operations                 |
| Failure handling     | Toast + tracker preserves history | Toast for attention, tracker for forensic detail                 |
| @catch_errors        | Adapted, no alert= param          | Backwards-compatible convenience for simple cases                |
| Technology           | Pure Solara                       | No legacy baggage, forward-looking                               |
