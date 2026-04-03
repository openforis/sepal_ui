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
┌──────────── NotificationBus (kernel-scoped, per session) ─────────────┐
│  toasts: solara.reactive([])      tasks: solara.reactive([])          │
├───────────────────────────────────────────────────────────────────────-┤
│                                                                       │
│  Publishers:                     Renderers:                           │
│  ├─ use_notifications() hook     ├─ ToastStack (floating, top-right)  │
│  ├─ notify() global (resolves    ├─ TaskProgressPill (floating,       │
│  │  current kernel context)      │    bottom-left) — primary          │
│  └─ @catch_errors decorator      └─ TaskProgressStrip — follow-up     │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

### Session Scoping

The notification bus MUST be kernel-scoped, not global. pysepal's Solara runtime keys sessions by kernel ID via `solara.server.kernel_context.get_current_context().kernel` (see `session_manager.py`).

**Implementation:** `NotificationProvider` creates a `NotificationBus` instance using `solara.use_reactive()` inside the component — Solara reactives created within component scope are automatically kernel-scoped. The bus is exposed to children via Solara's `provide`/`use_context` pattern (same as React context).

**Global `notify()` resolution:** The global escape hatch resolves the current kernel's bus by reading kernel context at call time. If called from a background thread, it captures the kernel context at task creation (closure) and schedules the update on the correct event loop.

**No-provider behavior:** If `notify()` or `use_notifications()` is called before a `NotificationProvider` is mounted (or after unmount), the call is a **no-op** and logs a warning via `logging.getLogger(__name__).warning(...)`. No buffering, no error — silent degradation with a log trail for debugging.

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

**Queue policies:**

- **Max retained:** 20 toasts in the queue. Beyond that, oldest non-error toasts are dropped.
- **Error rotation:** Persistent errors count toward the 3 visible slots, but after 30 seconds they auto-collapse to a compact "N errors" badge at the top of the stack, freeing slots for newer toasts. Clicking the badge expands the error list.
- **Deduplication:** Toasts with identical `(message, type)` within a 2-second window are merged. The duplicate increments a counter displayed as a badge on the toast (e.g., "x3") instead of creating a new entry.

## Layer 2: Task Progress

Persistent indicator for "something is happening" with structured milestone tracking.

**Primary renderer: TaskProgressPill.** The TaskProgressStrip (status bar variant) is deferred to a follow-up iteration — building both simultaneously adds scope without a concrete product reason.

### TaskProgressPill

- Small floating pill at bottom-left
- Collapsed: spinner icon + "N tasks running"
- Click to expand: mini-panel with task details
- Disappears when no tasks active

### Expanded Detail Panel

- Each task shows: title, current step message, overall progress bar
- Click a task to see full milestone timeline
- Failed tasks: red, show error message + milestone history preserved
- Cancelled tasks: grey, show last completed milestone
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


# Timeout defaults per type (seconds). None = persist until dismissed.
TOAST_TIMEOUT_DEFAULTS = {
    ToastType.SUCCESS: 5.0,
    ToastType.INFO: 5.0,
    ToastType.WARNING: 10.0,
    ToastType.ERROR: None,
}


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Toast:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message: str = ""
    type: ToastType = ToastType.INFO
    created_at: float = field(default_factory=time.time)
    timeout: Optional[float] = None  # Derived from TOAST_TIMEOUT_DEFAULTS if None
    count: int = 1  # Incremented on dedup merge


@dataclass(frozen=True)
class TaskMilestone:
    """A discrete named step in a task's execution (e.g., 'Validating geometry')."""
    message: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class TrackedTask:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    status: TaskStatus = TaskStatus.PENDING
    milestones: tuple[TaskMilestone, ...] = ()  # Immutable for reactive updates
    progress: Optional[float] = None  # 0.0-1.0, continuous, updated in place
    total_steps: Optional[int] = None  # If known, enables "step 2/5" display
    current_step: int = 0  # Current step index
    created_at: float = field(default_factory=time.time)
    error_message: Optional[str] = None
```

**Key design decisions:**

- `frozen=True` dataclasses for immutability. All state updates produce new instances.
- **Milestones vs progress are separate concerns:** `milestones` is a tuple of discrete named events (append-only, shown in timeline). `progress` is a single float updated frequently (shown as progress bar). This avoids the problem of every progress tick creating a new timeline entry.
- `total_steps` / `current_step` enable "step 2/5" display without deriving from milestone count.
- `CANCELLED` status covers explicit cancellation (user-initiated or unmount).
- **Reactive containers:** The bus stores `list[Toast]` and `list[TrackedTask]` in `solara.reactive()`. All mutations go through bus helper methods that enforce copy-on-write (e.g., `_update_task()` replaces the list with a new copy). Direct mutation of the reactive lists is never exposed to consumers.

### NotificationBus (kernel-scoped)

```python
class NotificationBus:
    """Owns notification state for a single kernel/session."""

    def __init__(self):
        self.toasts: solara.Reactive[list[Toast]] = solara.reactive([])
        self.tasks: solara.Reactive[list[TrackedTask]] = solara.reactive([])

    # --- Thread-safe mutation helpers (all produce new lists) ---
    def add_toast(self, toast: Toast) -> None: ...
    def remove_toast(self, toast_id: str) -> None: ...
    def add_task(self, task: TrackedTask) -> None: ...
    def update_task(self, task_id: str, **changes) -> None: ...
    def remove_task(self, task_id: str) -> None: ...
```

Mutations are **never** exposed as raw list access. All go through bus methods that do copy-on-write and schedule on the Solara event loop when called from threads.

## Publisher API

### Primary: `use_notifications()` hook

For use inside Solara components:

```python
@solara.component
def AoiView():
    notifications = use_notifications()

    async def process_aoi():
        with notifications.track("Processing AOI", total_steps=3) as task:
            task.step("Validating geometry...")        # milestone + current_step=1
            result = await gee_interface.get_info_async(obj)
            task.step("Fetching from GEE...")          # milestone + current_step=2
            task.set_progress(0.5)                     # continuous progress update
            data = await gee_interface.get_asset_async(asset_id)
            task.step("Clipping raster...")            # milestone + current_step=3
            task.set_progress(0.9)
        notifications.success("Assets loaded!")

    solara.lab.use_task(process_aoi, prefer_threaded=False, dependencies=None)
```

**`use_notifications()` returns a `Notifier` with:**

- `.success(msg)`, `.error(msg)`, `.warning(msg)`, `.info(msg)` — publish toasts
- `.track(title, total_steps=None) -> TaskTracker` — context manager for task progress
- `.dismiss(toast_id)` — manually dismiss a toast

**`TaskTracker` context manager:**

- `.step(msg)` — add a named milestone to the timeline, increment `current_step`
- `.set_progress(value: float)` — update continuous progress (0.0-1.0), does NOT create a milestone
- `.update(msg)` — update task title
- `.complete(msg=None)` — explicit completion (also auto-completes on `__exit__`)
- `.fail(msg)` — explicit failure (also auto-fails on exception)
- `.cancel()` — explicit cancellation

**Failure behavior:** On unhandled exception inside `with notifications.track(...)`:

- Task marked FAILED with milestone history preserved in tracker
- Error toast auto-published to grab attention
- User can inspect milestone details in expanded tracker panel

**Cancellation behavior:**

- `.cancel()` sets status to CANCELLED. Task stays in tracker (grey) with last milestone visible.
- On `NotificationProvider` unmount: running tasks are marked CANCELLED (not silently deleted).
- Integrates with `use_task`'s `.cancel()`: the tracker's `__exit__` checks for `asyncio.CancelledError` and maps to CANCELLED status.

### Escape hatch: `notify()` and `track_task()` global functions

For non-component code (decorators, scripts, background threads):

```python
from pysepal.solara.notifications import notify, track_task

# Toasts
notify("Export failed", type="error")
notify("File saved", type="success")

# Task tracking from background code
with track_task("Exporting to Drive", total_steps=2) as task:
    task.step("Preparing data...")
    task.set_progress(0.5)
    task.step("Uploading...")
```

Both `notify()` and `track_task()` resolve the current kernel's bus at call time. If called from a background thread, the kernel context must be captured at task creation via closure (same pattern as GEE async calls in this codebase).

### Adapted `@catch_errors` decorator

```python
@catch_errors  # No alert= param needed
def simple_process(self):
    do_something()
```

**Contract preservation (from current `decorator.py`):**

- Exceptions are **always re-raised** after publishing an error toast (preserves current behavior where `raise e` follows `alert_.add_msg()`).
- `SepalWarning` instances are filtered and published as warning toasts (one per warning). Other warnings continue through Python's standard warning mechanism via `custom_showwarning()`.
- Return value is passed through on success (unchanged).
- The `alert=` parameter is **deprecated but accepted** — if provided, the old behavior is used (backwards compat for incremental migration). If omitted, publishes to the notification bus.

## Integration with MapApp Shell

The current app shell is a hybrid ipyvuetify `VuetifyTemplate` (`MapApp.vue`) with:

- A map container (fixed position)
- A left navigation drawer (step list, links, theme toggle)
- A right panel (`RightPanel.vue`) with its own scroll region and toggle tab
- Step content overlaying the map

### Mount strategy

`NotificationProvider` is placed **inside** the `@solara.component` Page function, at the same level as `MapApp.element()`. It renders **outside** the MapApp Vue template using Solara's own DOM, avoiding z-index conflicts with the Vue-managed layout.

```python
@solara.component
def Page():
    with solara.Column():  # or solara.Div()
        MapApp.element(...)
        NotificationProvider(progress_style="pill")
```

### Positioning and z-index

- **ToastStack:** CSS `position: fixed`, `top: 16px`, `right: 16px`, `z-index: 1000` (above MapApp's Vue shell which uses standard Vuetify z-indices). Width constrained to ~350px so it doesn't overlap the right panel toggle tab.
- **TaskProgressPill:** CSS `position: fixed`, `bottom: 16px`, `left: 16px`, `z-index: 1000`. Small enough to avoid the left nav drawer.
- Both use `pointer-events: none` on the container with `pointer-events: auto` on individual cards, so clicks pass through to the map.

## File Structure

```
pysepal/solara/notifications/
├── __init__.py          # Public exports: use_notifications, notify, track_task,
│                        #   NotificationProvider, ToastStack, TaskProgressPill
├── state.py             # Toast, TrackedTask, TaskMilestone, enums, TOAST_TIMEOUT_DEFAULTS
├── bus.py               # NotificationBus (kernel-scoped), thread-safe mutation helpers
├── hook.py              # use_notifications(), Notifier, TaskTracker context manager
├── provider.py          # NotificationProvider component (creates bus, provides context)
├── toast_stack.py       # ToastStack component (dedup, queue, auto-dismiss)
├── task_pill.py         # TaskProgressPill component
└── globals.py           # notify(), track_task(), catch_errors adapter
```

**Deferred:**

- `task_strip.py` (TaskProgressStrip) — follow-up iteration after pill is validated

### Tests

```
tests/test_solara/test_notifications/
├── conftest.py          # Solara test harness setup (see Testing section)
├── test_state.py        # Dataclass immutability, copy-on-write
├── test_bus.py          # Bus mutations, thread-safe scheduling, kernel scoping
├── test_hook.py         # Hook, track context manager, cancel, cleanup
├── test_toast_stack.py  # Rendering, auto-dismiss, max 3, dedup, error rotation
├── test_task_pill.py    # Collapse/expand, milestone timeline, failure/cancel state
└── test_globals.py      # notify(), track_task(), catch_errors adapter
```

## Testing Strategy

**Prerequisite:** This project does not have an established `tests/test_solara` harness. The first implementation step must create this harness before writing notification tests.

**Harness approach:** Use `solara.test` utilities (or `solara.server.starlette.test_app` if needed) to create a test kernel context so that:

- `solara.reactive()` works as expected
- Kernel-scoped state is isolated between tests
- Components can be rendered and asserted on

**Priority test cases (hard cases first):**

1. Background-thread publish — `notify()` called from `asyncio.to_thread()`, verify it reaches the correct kernel's bus
2. Cancellation — task cancelled mid-execution, verify CANCELLED status and milestone preservation
3. Unmount during active work — `NotificationProvider` removed while tasks running, verify tasks marked CANCELLED
4. Duplicate error suppression — 10 identical errors in 1 second, verify dedup produces 1 toast with count=10
5. Burst notification load — 50 toasts in rapid succession, verify queue cap at 20 and no dropped errors
6. No-provider safety — `notify()` called with no mounted provider, verify no-op + warning log

## Decisions Log

| Decision              | Choice                                     | Rationale                                                                  |
| --------------------- | ------------------------------------------ | -------------------------------------------------------------------------- |
| Architecture          | Two components, one bus                    | Clean UX separation: toasts (ephemeral) vs progress (persistent)           |
| Session scoping       | Kernel-scoped bus via provider context     | Matches pysepal's SessionManager pattern; prevents cross-session leaks     |
| Toast position        | Floating top-right, fixed position         | Near the right panel where operations happen                               |
| Progress position     | Floating bottom-left pill                  | Left area underused, avoids clutter                                        |
| Progress renderers    | Pill first, strip deferred                 | One renderer until pill is validated; reduces scope                        |
| API style             | Hook + global escape hatch                 | Solara-native, with coverage for non-component code and background threads |
| Auto-dismiss          | Type-based                                 | Errors persist (critical), success fades (non-blocking)                    |
| Toast queue           | Max 20, dedup, error rotation at 30s       | Prevents starvation of newer toasts by persistent errors                   |
| Milestone vs progress | Separate APIs (step vs set_progress)       | Avoids noisy timelines from frequent progress ticks                        |
| Task lifecycle        | PENDING/RUNNING/COMPLETED/FAILED/CANCELLED | Matches existing codebase patterns (use_task, GEETask cancellation)        |
| Failure handling      | Toast + tracker preserves history          | Toast for attention, tracker for forensic detail                           |
| @catch_errors         | Adapted, preserves re-raise contract       | Exception always re-raised; SepalWarning filtered to warning toasts        |
| No-provider behavior  | No-op + warning log                        | Silent degradation; no crash, discoverable via logs                        |
| Technology            | Pure Solara                                | No legacy baggage, forward-looking                                         |
| Test harness          | New tests/test_solara/ with conftest       | Must be created first; no existing Solara test infrastructure              |
