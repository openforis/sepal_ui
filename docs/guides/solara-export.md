# Solara Export with pysepal

> Use this guide when a pysepal Solara app needs to let users export an
> `ee.Image` or `ee.FeatureCollection` to an Earth Engine asset, Google Drive,
> or the SEPAL workspace.

## What the Export Component Is

The export component is a single launcher button plus a modal dialog that
drives an async submission engine. It is designed to be dropped into any
pysepal Solara app that has GEE-produced layers users might want to take out
of the app.

It provides:

- one `ExportLauncher` button that opens a dialog
- a dialog that offers Earth Engine asset / Google Drive / SEPAL workspace as
  destinations, with kind-appropriate options (image scale or table format)
- an async engine that handles folder creation, task submission, Drive
  staging for SEPAL targets, and cleanup
- a controller hook (`use_export_dialog`) for when you need to drive the
  dialog from a custom layout instead of the default launcher button
- per-source deferred resolution so heavy `ee` computations only fire when
  the user actually presses Export

It does **not** provide:

- `ee.ImageCollection` export — host apps must collapse to a single
  `ee.Image` (e.g. with `.toBands()` or `.mosaic()`) before passing in
- interactive visualization or symbology editing
- a replacement for custom export flows that have their own UX
  requirements — the controller hook is the extension point

## Core Pieces

The public surface lives in `pysepal.solara.components.export`:

- `ExportLauncher` — the drop-in button + dialog component
- `ExportSource` — dataclass declaring one exportable layer
- `ResolvedExport` — dataclass returned by an `ExportSource.resolve()` call;
  carries the concrete `ee` object and per-source defaults
- `use_export_dialog(sources, …)` — controller hook (advanced layouts)
- `ExportDialog` — the modal UI (used by `ExportLauncher`; also composable)
- `submit_export_request(request, …)` — headless async submitter
- `ExportResult` — structured return after a successful submission
- `TABLE_FILE_FORMATS`, `DEFAULT_TABLE_FILE_FORMAT`,
  `DEFAULT_IMAGE_FILE_FORMAT` — canonical file-format constants

Conceptually:

1. The parent declares a tuple of `ExportSource` objects.
2. The parent renders `ExportLauncher(sources=...)`.
3. The user clicks the button, picks an asset and destination, presses
   Export.
4. The engine submits the EE task and (for SEPAL targets) copies the
   result file(s) from Drive into the workspace.
5. A success/error toast is published through `NotificationProvider`.

## Quickstart: One Source, One Button

```python
import ee
import solara

from pysepal.solara.components.export import ExportLauncher, ExportSource, ResolvedExport
from pysepal.solara.notifications import NotificationProvider


@solara.component
def ExportsPanel(aoi: solara.Reactive[ee.Geometry]):
    def _resolve_elevation() -> ResolvedExport:
        dem = ee.Image("USGS/SRTMGL1_003").clip(aoi.value)
        return ResolvedExport(
            ee_object=dem,
            default_name="SRTM_elevation",
            region=aoi.value,
            default_scale=30,
        )

    sources = (
        ExportSource(
            id="srtm-elevation",
            label="SRTM elevation (m)",
            kind="image",
            resolve=_resolve_elevation,
        ),
    )

    ExportLauncher(sources=sources, button_text=True)
```

Drop `NotificationProvider()` once in your app shell so the dialog has a
place to publish success and error toasts. The notifications guide covers
that pattern in full: see [`solara-notifications.md`](solara-notifications.md).

## Declaring an `ExportSource`

`ExportSource` is the parent-owned description of one exportable layer.

```python
ExportSource(
    id="elevation",              # stable identifier, used as the Select value
    label="SRTM elevation",       # user-visible label in the dropdown
    kind="image",                 # "image" or "table" — must match what resolve() returns
    resolve=_resolve_elevation,   # 0-arg callable, runs when user presses Export
    description="",               # optional, currently unused in UI
    disabled=False,               # greyed out in the Select when True
    icon="",                       # optional mdi- icon name for future use
)
```

Key rule: **`resolve` is called lazily**, not at mount. This is deliberate —
your factory can stitch together `ee` objects that depend on the live AOI or
other reactive state, and the computation only fires when the user commits
to an export. Keep the factory pure-ish: it should return a `ResolvedExport`
or raise on a clear error.

If `resolve()` raises, the dialog surfaces the exception message via the
notification system (falling back to an inline `solara.Warning` when no
provider is mounted).

## What `ResolvedExport` Carries

`ResolvedExport` is the concrete payload the engine needs to submit the job.

```python
ResolvedExport(
    ee_object=ee_object,             # ee.Image or ee.FeatureCollection
    default_name="my_export",         # pre-fills the Export name field
    region=aoi.value,                 # optional, used for image exports
    default_scale=30,                 # optional, used for image exports
    selectors=("ADM0_NAME",),          # optional, narrow table columns
    gee_folder="my_module",           # optional, relative to user's asset root
    drive_folder="",                  # optional, Drive folder name
    sepal_folder="exports",           # optional, relative to module_results
    table_file_format="SHP",         # canonical enum; see below
    image_file_format="GEO_TIFF",    # canonical enum; see below
    max_pixels=1_000_000_000,
    max_vertices=None,
    priority=None,
    vis_params=None,                  # optional SEPAL viz to embed on image exports
)
```

The user can override any destination-related field in the dialog. The
`default_*` values just pre-fill the controls.

## Carrying SEPAL Visualization Onto Exports

When an app renders a styled `ee.Image` on the map and then exports the
underlying classification (e.g. with `SepalMap.add_ee_layer(image, vis_params)`),
the exported Earth Engine asset will not carry that styling — `vis_params`
lives on the `EELayer`, not on the image. SEPAL's convention is to encode
styling as image properties named `visualization_<index>_<key>`; SepalMap
reads them on display, and Earth Engine asset exports preserve them, so any
downstream consumer (another SEPAL recipe, the Code Editor) sees the styling
automatically.

Pass `vis_params` to `ResolvedExport` to opt into this:

```python
GFC_VIS_PARAMS = {
    "name": "loss_year",
    "type": "categorical",
    "bands": ["classification"],
    "palette": HEX_PALETTE,
    "values": [*range(1, GFC_MAX_YEAR + 1), 30, 40, 50, 51],
    "labels": ["loss 2001", ..., "non forest", "stable forest", "gain", "gain + loss"],
}

ExportSource(
    id="gfc_classified",
    label="GFC classified image",
    kind="image",
    resolve=lambda: ResolvedExport(
        ee_object=classification,
        default_name="gfc",
        region=aoi.geometry(),
        default_scale=30,
        vis_params=GFC_VIS_PARAMS,
    ),
)
```

The dict shape mirrors the kwargs of
`pysepal.mapping.visualization.set_viz_params` (the writer; inverse of
`get_viz_params` used by SepalMap on display). Keys:

| Key        | Type                                              | Notes                                                   |
| ---------- | ------------------------------------------------- | ------------------------------------------------------- |
| `name`     | `str`                                             | Logical name. Defaults to `"default"`.                  |
| `type`     | `"continuous" \| "categorical" \| "rgb" \| "hsv"` | SepalMap infers from band count when omitted.           |
| `bands`    | `Sequence[str]`                                   | One band for continuous/categorical; three for rgb/hsv. |
| `min`      | scalar or `Sequence[float]`                       | Per-band minimum(s).                                    |
| `max`      | scalar or `Sequence[float]`                       | Per-band maximum(s).                                    |
| `palette`  | `Sequence[str]` or comma-joined string            | Hex colors.                                             |
| `values`   | `Sequence[int]`                                   | Categorical class codes (palette[i] maps to values[i]). |
| `labels`   | `Sequence[str]`                                   | Legend labels.                                          |
| `inverted` | `Sequence[bool]`                                  | Per-band inversion flags.                               |

Only applies to image-kind exports; ignored on table-kind sources. For
multiple named visualizations on the same image, write them eagerly via
`set_viz_params(image, ..., index=N)` before passing to `ResolvedExport`.

## Destinations

The dialog offers three destinations, each enabled based on runtime state:

- **Earth Engine asset** (`gee`) — default. Submits
  `projects.image.export` / `projects.table.export` to the user's EE project
  asset root. The dialog shows a live preview hint:
  `Will be exported as: projects/<user>/assets/<folder>/<name>`.
- **Google Drive** (`drive`) — submits a Drive export task; no waiting for
  completion inside the dialog.
- **SEPAL workspace** (`sepal`) — requires a session-backed `SepalClient`.
  Exports to Drive first, waits for completion, downloads the files, and
  uploads them under `<module_results>/<sepal_folder>/`. Disabled (greyed
  out) when `sepal_client` is None — i.e. when the app is not running
  inside a SEPAL session.

SEPAL workspace exports must stay on the `SepalClient` path. Do not stage,
copy, or rewrite user export files in the container filesystem from host app
code; let the export engine download bytes from Drive and upload them through
`sepal_client.set_file(...)`.

The engine creates any missing intermediate folders under the user's asset
root before submitting an EE asset export.

## File Formats: Use Canonical Enum Values

ee-client's pydantic models validate file formats strictly. **Use the
canonical REST-API enum strings**, not the human-friendly sepal_ui names:

| What users see | What to store as `value` |
| -------------- | ------------------------ |
| GeoTIFF        | `"GEO_TIFF"`             |
| GeoJSON        | `"GEO_JSON"`             |
| Shapefile      | `"SHP"`                  |
| CSV            | `"CSV"`                  |
| KML / KMZ      | `"KML"` / `"KMZ"`        |

The constants `DEFAULT_IMAGE_FILE_FORMAT = "GEO_TIFF"` and
`DEFAULT_TABLE_FILE_FORMAT = "SHP"` already use the canonical values;
`TABLE_FILE_FORMATS` maps friendly text labels to canonical values so users
still see `"GeoJSON"` in the dropdown but the wire payload is `"GEO_JSON"`.

Requires **ee-client >= 2.5.2** (enforced by pyproject.toml). 2.5.1 had a
bug where the table→asset serializer emitted `driveExportOptions` for asset
exports; 2.5.2 renamed it to `assetExportOptions`.

## Multiple Sources

Pass a tuple with more than one entry and the dialog groups them by kind in
the Asset dropdown, with subheaders and a divider between `Images` and
`Feature collections`:

```python
sources = (
    ExportSource(id="dem",    label="Elevation (DEM)", kind="image", resolve=_resolve_dem),
    ExportSource(id="slope",  label="Slope (degrees)",  kind="image", resolve=_resolve_slope),
    ExportSource(id="aoi",    label="AOI polygons",      kind="table", resolve=_resolve_aoi),
    ExportSource(id="points", label="Sample points",     kind="table", resolve=_resolve_points),
)
ExportLauncher(sources=sources, button_text=True)
```

When only one kind is present, the grouping and subheader are suppressed
and the list renders flat — no need to do anything special for single-kind
apps.

To keep a layer visible but non-selectable (e.g., not ready yet), set
`disabled=True` on that `ExportSource`.

## The Dialog Body is Always Visible

When no asset is selected, the Destination radio, Name field, and folder
fields render but are disabled. The rationale is that users should see the
structure of the form before committing to a selection — it telegraphs
which options exist.

Kind-specific widgets (image scale presets, table file format) only appear
after a source is selected, because they are mutually exclusive — showing
both would be misleading.

The Export button stays disabled until a source is selected and the name
field is non-empty.

## Custom Layouts: `use_export_dialog`

When the default `ExportLauncher` button doesn't fit — e.g., you want the
trigger to live inside a toolbar menu, or you need to render the dialog
from multiple trigger points — use the controller hook directly:

```python
from pysepal.solara.components.export import ExportDialog, use_export_dialog

@solara.component
def CustomExportsToolbar(sources):
    controller = use_export_dialog(sources=sources)

    solara.Button(
        label="Export…",
        icon_name="mdi-tray-arrow-down",
        on_click=controller.open_dialog,
    )
    ExportDialog(controller=controller, title="Export layers")
```

`ExportDialogController` exposes everything you might want to drive from the
outside:

- `open` / `open_dialog()` / `close_dialog()` — dialog open state
- `selected_target` / `selected_source_id` / `export_name` — reactive inputs
- `task` — the underlying `solara.lab.use_task` handle (for pending/finished)
- `result` — the last `ExportResult`
- `submit_export()` / `cancel_export()` — programmatic controls
- `sources` — the resolved tuple of `ExportSource`

Keep the hook invocation unconditional at the top of the component — it
registers solara reactives and effects per the usual rules of hooks.

## Notifications and Timeouts

On submission outcome the dialog publishes one toast through the notifier
returned by `use_notifications()`:

- success → `Notifier.success(message, timeout=EXPORT_SUCCESS_TOAST_TIMEOUT)`
- error → `Notifier.error(exception_message)`
- cancel → `Notifier.cancel("Export cancelled.")` (or a local-wait message
  if the remote task is still running)

The success toast uses a longer timeout (8s by default, vs the 3s global
default) because it carries a copyable asset path or task id. Tune the
constant in `pysepal/solara/components/export_hook.py:EXPORT_SUCCESS_TOAST_TIMEOUT`
if your app wants a different duration.

All `Notifier` methods accept an optional `timeout` kwarg for per-call
control:

```python
notifications = use_notifications()
notifications.success("Export submitted", timeout=12.0)
notifications.warning("Almost done…")  # uses type default (3s)
```

When no `NotificationProvider` is mounted, the dialog falls back to an
inline `solara.Success` / `solara.Error` / etc. rendered inside the card.

## The Modal Stays Open After Success

The dialog does NOT auto-close when the task completes. This is
intentional: users often want to copy the resulting asset path, note the
task id, or fire off a second export with slightly different options.
Users close the dialog themselves.

If your app needs the old auto-close behavior, set `controller.open.value = False`
inside your own `use_effect` watching `controller.result.value`.

## Testing Components That Render `ExportLauncher`

Two test-side helpers live in `tests/test_solara/test_export_component.py`:

```python
def _render(factory, *args, **kwargs):
    """Render a Solara widget with a running event loop so ``use_task`` can schedule."""
    async def _runner():
        return factory(*args, **kwargs)
    return asyncio.run(_runner())


def _render_preselected_dialog(source, *, target="gee"):
    """Render ExportDialog with a source preselected and the dialog open."""
    @solara.component
    def _Harness():
        controller = use_export_dialog(
            sources=[source],
            gee_interface=MagicMock(),
            drive_interface=MagicMock(),
        )
        def _preselect():
            controller.selected_source_id.set(source.id)
            controller.selected_target.set(target)
            controller.open.set(True)
        solara.use_effect(_preselect, [])
        return ExportDialog(controller=controller, title="Test")
    async def _runner():
        return _Harness.widget()
    return asyncio.run(_runner())
```

Key points:

- `.widget()` in a synchronous test fails with
  `RuntimeError: no running event loop` because Solara's `use_task`
  schedules via `asyncio.create_task`. Wrap the render in `asyncio.run` to
  provide a loop during the mount.
- Post-selection contracts (e.g. "destination is a RadioGroup", "image
  scale uses BtnToggle not a Slider") require the dialog to be in a
  selected state. The preselection harness drives the controller there
  before the walk.

## Wire Into the Default Scaffold

When scaffolding a new pysepal Solara app that produces exportable GEE
layers:

- mount `NotificationProvider()` once in the app shell (see the
  notifications guide)
- collect the app's exportable layers into a tuple of `ExportSource`
  objects, with `resolve` reading from your AppState or props
- drop `ExportLauncher(sources=sources)` into the right side panel or
  toolbar — use `button_text=True` inside collapsible panels where the
  pysepal convention is `small=True, block=True`
- avoid building a second custom export UX unless the dialog cannot cover
  your requirements; in that case prefer the `use_export_dialog` hook over
  re-implementing submission logic

The reference integration lives at
`pysepal/templates/solara/solara_map_app/aoi_all_methods_mapapp.py`.
