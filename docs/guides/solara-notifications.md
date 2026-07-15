# Solara Notifications with pysepal

> Use this guide when a pysepal Solara app needs user-facing toast notifications,
> running-task status, or a shared floating notification UI.

## What the Notification System Is

The pysepal notification system is a kernel-scoped, in-memory UI notification
layer for Solara apps.

It provides:

- toast notifications for success, info, warning, error, and cancel states
- a floating task pill for active work
- a task log derived from tracked task history
- a Vue-backed overlay that integrates with `MapApp`

It does **not** provide:

- durable event storage
- cross-kernel or cross-process messaging
- audit logging
- guaranteed delivery after kernel restart

Use it for live app UX, not for backend workflow persistence.

## Core Pieces

The main API lives in `pysepal.solara.notifications`:

- `NotificationProvider` — mounts the notification UI and owns the kernel-scoped bus
- `use_notifications()` — returns a `Notifier` bound to the current kernel bus
- `notify()` and `track_task()` — global escape hatches for non-component code
- `Notifier.track(...)` — returns a `TaskTracker` context manager for long-running work

Conceptually:

1. `NotificationProvider()` mounts once at app-shell level.
2. Components call `use_notifications()`.
3. Components publish toasts or tracked tasks.
4. The notification UI reacts to the shared bus state.

## Scope Rules

The isolation boundary is the live app runtime session, not the route.
Notifications are scoped to the current app runtime in three contexts:

- Solara server apps launched with `solara run`
- Voila apps launched from a notebook kernel
- Plain Jupyter Notebook/Lab, scoped to the active notebook kernel

- One browser page connection usually maps to one Solara virtual kernel under `solara run`.
- Voila and Jupyter scope to the active notebook kernel.
- The notification bus is keyed by the pysepal runtime session id.
- Routes inside the same live page share the same notification history.
- Separate browser page loads get separate kernels and therefore separate histories.

This means:

- mount one provider per app shell
- allow many consumers to call `use_notifications()`
- do not assume route changes create isolated notification buses

If an app launcher opens `/fcdm` and `/basin-rivers` as separate pages, each app
gets its own history. If those are route transitions inside one live page, they
share the same history.

## Mounting Pattern

Mount `NotificationProvider()` once near the top of the app shell.

### Single-page app

```python
@solara.component
@with_sepal_sessions(module_name="my_app")
def Page():
    setup_theme_colors()
    NotificationProvider()
    AppContent()
```

### Multipage app with shared layout

If all routes should share one notification surface, mount the provider in the
shared layout instead of inside each page.

```python
@solara.component
def Layout(children=[]):
    NotificationProvider()
    solara.Column(children=children)
```

### Voila apps

Voila apps use the same mounting pattern:

```python
@solara.component
def Page():
    NotificationProvider()
    AppContent()
```

The provider uses the active Voila notebook kernel as the notification bus
scope. No Solara server context is created or required.

### What not to do

Do not mount a separate provider in every page if those pages can coexist in the
same kernel. The bus is shared anyway, and multiple providers can render
multiple overlays against the same state.

## Using `use_notifications()` Inside Components

The normal component pattern is:

```python
from pysepal.solara.notifications import NotificationProvider, use_notifications

@solara.component
def ResultsPanel():
    notifications = use_notifications()

    def handle_ready():
        notifications.success("Results loaded")
```

Toast methods:

- `success(message)`
- `info(message)`
- `warning(message)`
- `error(message)`
- `cancel(message)`
- `dismiss(toast_id)`

If no provider is mounted, `use_notifications()` returns a `NoopNotifier`.
That means toast calls are silently dropped unless the component provides its own
fallback UX.

## Tracking Long-Running Tasks

Use `notifications.track(...)` together with `solara.lab.use_task` for
non-blocking work.

```python
@solara.component
def StatsPanel():
    notifications = use_notifications()
    gee_interface = get_current_gee_interface()

    @solara.lab.use_task(
        dependencies=None,
        raise_error=False,
        prefer_threaded=False,
    )
    async def run_job(request):
        with notifications.track("Loading statistics", total_steps=3) as task:
            task.step("Validating input")
            task.step("Querying Earth Engine")
            result = await gee_interface.get_info_async(request.ee_object)
            task.step("Formatting result")
            return result
```

Use task tracking when:

- the work is async or long-running
- the user benefits from a visible running-state indicator
- you want a task log instead of only final toasts

Use plain toasts when:

- the event is immediate
- there is no meaningful progress to report

## Recommended Async Pattern

For new GEE-based Solara apps:

- use `solara.reactive()` AppState
- use `solara.lab.use_task(..., prefer_threaded=False)`
- snapshot request inputs before starting work
- use `notifications.track(...)` inside the task body
- mirror task results back into AppState in `solara.use_effect`

This matches the current session-backed async GEE path and avoids loop-hopping
problems.

## Fallback UX When No Provider Exists

If a component can be used inside or outside a shell that mounts
`NotificationProvider()`, do not assume the notifier is active.

Preferred fallback pattern:

- detect whether `use_notifications()` returned a `NoopNotifier`
- still surface success/error/cancel inline if the provider is absent
- reserve silent no-op behavior for utility-level code where inline feedback is
  impossible

The AOI Solara component is the reference example for this pattern.

## Global Escape Hatches

Use these only when you cannot conveniently call `use_notifications()` from a
component:

- `notify(message, type_="info")`
- `track_task(title, total_steps=None)`

Caveats:

- they still resolve the current kernel bus
- if no provider is mounted, `notify()` logs a warning and drops the toast
- if no provider is mounted, `track_task()` returns a no-op tracker

Prefer component-local `use_notifications()` whenever possible.

## MapApp Integration

The notification UI is designed to coexist with `MapApp`.

`MapApp.vue` publishes CSS custom properties such as
`--sepal-notification-right-offset`, and the Vue notification UI uses them to
position the task pill relative to the right panel.

Practical rule:

- if the app uses `MapApp`, mount `NotificationProvider()` in the same page or
  shell so the overlay can consume the active layout variables

## Safety and Limits

The notification system is safe for live, per-kernel app UX.

It is not a replacement for durable logs or event infrastructure.

Important limits:

- state is in-memory only
- restart the kernel and history is lost
- identical toasts are deduplicated within a short time window
- only the newest error toast is retained in the toast queue
- only the newest few toasts are visible in the overlay
- finished task history is capped and older finished tasks are pruned

## Default Scaffold Rule

When building a new pysepal Solara app that has async work or user-visible
status transitions:

- mount `NotificationProvider()` once in the app shell
- use `use_notifications()` inside pages and major tiles
- use `notifications.track(...)` for long-running jobs
- use final success/error/cancel toasts for task completion state
- do not build a second custom alert system unless the app has a very specific
  UX reason
