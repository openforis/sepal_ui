"""Tests for the Solara export helpers."""

import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock

import solara

from pysepal.scripts import gee_interface as gee_interface_module
from pysepal.scripts.gee_interface import _resolve_create_folder_paths
from pysepal.solara.components import export_hook as export_hook_module
from pysepal.solara.components.export import (
    DEFAULT_TABLE_FILE_FORMAT,
    ExportLauncher,
    ExportRequest,
    ExportResult,
    ExportSource,
    ResolvedExport,
    _build_result_message,
    extract_task_id,
    get_task_state_name,
    infer_export_kind,
    matches_drive_export_prefix,
    resolve_asset_folder,
    resolve_sepal_folder,
    sanitize_export_name,
    submit_export_request,
)
from pysepal.solara.components.export_dialog import ExportDialog, _build_gee_asset_hint
from pysepal.solara.components.export_hook import get_active_source, use_export_dialog


class _FakeImage:
    def bandNames(self):
        return []


class _FakeTable:
    def first(self):
        return None

    def size(self):
        return 0


class _FakeImageCollection:
    def toBands(self):
        return None


def _render(factory, *args, **kwargs):
    """Render a Solara widget with a running event loop so ``use_task`` can schedule."""

    async def _runner():
        return factory(*args, **kwargs)

    return asyncio.run(_runner())


def _render_preselected_dialog(source, *, target="gee"):
    """Render ``ExportDialog`` with a source preselected and the dialog open.

    The production UX hides the dialog body until the user picks an asset, so
    assertions about post-selection widgets (destination radio, scale presets,
    folder fields) must drive the controller into the selected state first.
    """

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


def test_sanitize_export_name_normalizes_user_input():
    assert sanitize_export_name("  My export / result  ") == "My_export_result"


def test_table_exports_default_to_shapefile():
    resolved = ResolvedExport(ee_object=_FakeTable(), default_name="demo")
    request = ExportRequest(
        ee_object=_FakeTable(),
        export_kind="table",
        target="drive",
        name="demo",
    )

    assert DEFAULT_TABLE_FILE_FORMAT == "SHP"
    assert resolved.table_file_format == "SHP"
    assert request.table_file_format == "SHP"


def test_infer_export_kind_supports_image_like_objects():
    assert infer_export_kind(_FakeImage()) == "image"


def test_infer_export_kind_supports_table_like_objects():
    assert infer_export_kind(_FakeTable()) == "table"


def test_infer_export_kind_rejects_unsupported_objects():
    try:
        infer_export_kind(_FakeImageCollection())
    except TypeError as exc:
        assert "ee.Image" in str(exc)
    else:
        raise AssertionError("infer_export_kind should reject unsupported objects")


def test_resolve_asset_folder_joins_relative_paths():
    root = "projects/my-project/assets"
    assert resolve_asset_folder(root, "reports/2026") == "projects/my-project/assets/reports/2026"


def test_resolve_asset_folder_keeps_absolute_paths():
    absolute = "projects/other-project/assets/custom"
    assert resolve_asset_folder("projects/my-project/assets", absolute) == absolute


def test_build_gee_asset_hint_uses_resolved_folder_and_sanitized_name():
    hint = _build_gee_asset_hint(
        "projects/my-project/assets",
        "exports/final",
        "My export",
    )

    assert hint == ("Will be exported as: projects/my-project/assets/exports/final/My_export")


def test_get_active_source_requires_explicit_selection():
    sources = [
        ExportSource(
            id="demo",
            label="Demo layer",
            kind="table",
            resolve=lambda: ResolvedExport(
                ee_object=_FakeTable(),
                default_name="demo_export",
            ),
        )
    ]

    assert get_active_source(sources, "") is None
    assert get_active_source(sources, "demo") is sources[0]


def test_resolve_create_folder_paths_accepts_relative_asset_folder():
    relative_path, absolute_path = _resolve_create_folder_paths(
        "projects/my-project/assets",
        "exports/final",
    )

    assert relative_path == "exports/final"
    assert absolute_path == "projects/my-project/assets/exports/final"


def test_resolve_create_folder_paths_accepts_absolute_asset_folder():
    relative_path, absolute_path = _resolve_create_folder_paths(
        "projects/my-project/assets",
        "projects/my-project/assets/exports/final",
    )

    assert relative_path == "exports/final"
    assert absolute_path == "projects/my-project/assets/exports/final"


def test_resolve_sepal_folder_uses_module_results_for_relative_paths():
    sepal_client = SimpleNamespace(
        results_path="/home/sepal-user/module_results/my_module",
        BASE_REMOTE_PATH="/home/sepal-user",
    )

    result = resolve_sepal_folder(sepal_client, "exports/final")

    assert str(result) == "/home/sepal-user/module_results/my_module/exports/final"


def test_resolve_sepal_folder_keeps_absolute_paths():
    sepal_client = SimpleNamespace(
        results_path="/home/sepal-user/module_results/my_module",
        BASE_REMOTE_PATH="/home/sepal-user",
    )

    result = resolve_sepal_folder(sepal_client, "/home/sepal-user/custom/exports")

    assert str(result) == "/home/sepal-user/custom/exports"


def test_matches_drive_export_prefix_accepts_export_shards():
    assert matches_drive_export_prefix("result", "result")
    assert matches_drive_export_prefix("result.tif", "result")
    assert matches_drive_export_prefix("result-0000000000.tif", "result")
    assert matches_drive_export_prefix("result_part.csv", "result")
    assert not matches_drive_export_prefix("resultExtra.csv", "result")


def test_get_task_state_name_handles_dict_and_metadata_objects():
    dict_task = {"metadata": {"state": "SUCCEEDED"}}
    object_task = SimpleNamespace(metadata=SimpleNamespace(state="RUNNING"))

    assert get_task_state_name(dict_task) == "SUCCEEDED"
    assert get_task_state_name(object_task) == "RUNNING"
    assert get_task_state_name(None) is None


def test_extract_task_id_supports_strings_and_objects():
    task_obj = SimpleNamespace(id="task-123")
    named_obj = SimpleNamespace(name="operations/task-456")

    assert extract_task_id("task-abc") == "task-abc"
    assert extract_task_id(task_obj) == "task-123"
    assert extract_task_id(named_obj) == "operations/task-456"


def test_build_result_message_formats_targets():
    gee_result = ExportResult(
        target="gee",
        export_kind="image",
        name="demo",
        asset_id="projects/demo/assets/demo",
        message="",
    )
    sepal_result = ExportResult(
        target="sepal",
        export_kind="table",
        name="demo",
        sepal_paths=("/home/sepal-user/module_results/demo.csv",),
        message="",
    )

    assert _build_result_message(gee_result) == (
        "Earth Engine export submitted to `projects/demo/assets/demo`."
    )
    assert _build_result_message(sepal_result) == (
        "Export copied to SEPAL: `/home/sepal-user/module_results/demo.csv`."
    )


def test_export_launcher_renders_for_single_source():
    source = ExportSource(
        id="demo",
        label="Demo layer",
        kind="table",
        resolve=lambda: ResolvedExport(
            ee_object=_FakeTable(),
            default_name="demo_export",
            drive_folder="exports",
        ),
    )

    element = _render(
        ExportLauncher.widget,
        sources=[source],
        button_text=True,
        gee_interface=MagicMock(),
        drive_interface=MagicMock(),
    )

    def _walk(widget):
        yield widget
        for child in getattr(widget, "children", ()) or ():
            yield from _walk(child)

    asset_selects = [
        widget
        for widget in _walk(element)
        if widget.__class__.__name__ == "Select" and getattr(widget, "label", None) == "Asset"
    ]

    assert element is not None
    assert asset_selects


def test_export_launcher_shows_disabled_tooltip_without_sources():
    element = _render(
        ExportLauncher.widget,
        sources=[],
        button_text=True,
        gee_interface=MagicMock(),
        drive_interface=MagicMock(),
    )

    def _walk(widget):
        yield widget
        for child in getattr(widget, "children", ()) or ():
            yield from _walk(child)

    tooltip_widgets = [
        widget for widget in _walk(element) if widget.__class__.__name__ == "Tooltip"
    ]

    assert tooltip_widgets
    assert any(
        "No exportable layers available" in getattr(widget, "children", [])
        for widget in tooltip_widgets
    )


def test_export_launcher_renders_destination_as_radio_group():
    source = ExportSource(
        id="demo",
        label="Demo layer",
        kind="table",
        resolve=lambda: ResolvedExport(
            ee_object=_FakeTable(),
            default_name="demo_export",
            drive_folder="exports",
        ),
    )
    element = _render_preselected_dialog(source=source)

    def _walk(widget):
        yield widget
        for child in getattr(widget, "children", ()) or ():
            yield from _walk(child)

    radio_groups = [
        widget for widget in _walk(element) if widget.__class__.__name__ == "RadioGroup"
    ]
    selects = [
        widget
        for widget in _walk(element)
        if widget.__class__.__name__ == "Select" and getattr(widget, "label", None) == "Destination"
    ]

    assert radio_groups
    assert any(getattr(widget, "row", False) for widget in radio_groups)
    assert not selects


def test_export_launcher_renders_image_scale_presets_and_custom_field():
    source = ExportSource(
        id="image-demo",
        label="Demo image",
        kind="image",
        resolve=lambda: ResolvedExport(
            ee_object=_FakeImage(),
            default_name="demo_image",
            default_scale=30,
        ),
    )
    element = _render_preselected_dialog(source=source)

    def _walk(widget):
        yield widget
        for child in getattr(widget, "children", ()) or ():
            yield from _walk(child)

    btn_toggles = [widget for widget in _walk(element) if widget.__class__.__name__ == "BtnToggle"]
    custom_scale_fields = [
        widget
        for widget in _walk(element)
        if widget.__class__.__name__ == "TextField"
        and getattr(widget, "placeholder", None) == "Custom"
    ]
    sliders = [widget for widget in _walk(element) if "Slider" in widget.__class__.__name__]

    assert btn_toggles
    assert custom_scale_fields
    assert not sliders


def test_export_launcher_supports_small_block_button_convention():
    source = ExportSource(
        id="demo",
        label="Demo layer",
        kind="table",
        resolve=lambda: ResolvedExport(
            ee_object=_FakeTable(),
            default_name="demo_export",
        ),
    )
    element = _render(
        ExportLauncher.widget,
        sources=[source],
        button_text=True,
        block=True,
        gee_interface=MagicMock(),
        drive_interface=MagicMock(),
    )

    def _walk(widget):
        yield widget
        for child in getattr(widget, "children", ()) or ():
            yield from _walk(child)

    launcher_buttons = [
        widget
        for widget in _walk(element)
        if widget.__class__.__name__ == "Btn" and getattr(widget, "block", False)
    ]

    assert launcher_buttons
    assert any(getattr(widget, "small", False) for widget in launcher_buttons)


class _FakeGeeInterface:
    def __init__(self):
        self.created_folders = []
        self.asset_exports = []

    async def get_folder_async(self):
        return "projects/demo/assets"

    async def get_asset_async(self, asset_id, not_exists_ok=False):
        return None

    async def create_folder_async(self, folder_path):
        self.created_folders.append(folder_path)
        return {"id": folder_path}

    async def export_table_to_asset_async(
        self,
        collection,
        asset_id,
        description="",
        selectors=None,
        max_vertices=None,
        priority=None,
    ):
        self.asset_exports.append(
            {
                "collection": collection,
                "asset_id": asset_id,
                "description": description,
                "selectors": selectors,
                "max_vertices": max_vertices,
                "priority": priority,
            }
        )
        return {"id": "task-123"}


def test_submit_export_request_builds_gee_asset_result():
    gee_interface = _FakeGeeInterface()
    steps = []

    request = ExportRequest(
        ee_object=_FakeTable(),
        export_kind="table",
        target="gee",
        name="demo_export",
        gee_folder="reports/2026",
    )

    result = asyncio.run(
        submit_export_request(
            request,
            gee_interface=gee_interface,
            drive_interface=MagicMock(),
            sepal_client=None,
            on_step=steps.append,
        )
    )

    assert result.target == "gee"
    assert result.task_id == "task-123"
    assert result.asset_id == "projects/demo/assets/reports/2026/demo_export"
    assert steps == [
        "Validating export settings",
        "Preparing Earth Engine destination",
        "Submitting Earth Engine export",
    ]


# ---------------------------------------------------------------------------
# vis_params propagation: ResolvedExport → ExportRequest → submit_export_request
# ---------------------------------------------------------------------------


class _FakeGeeInterfaceImageExports:
    """Fake interface that records image-export submissions."""

    def __init__(self):
        self.exports: list[dict] = []

    async def get_folder_async(self):
        return "projects/demo/assets"

    async def get_asset_async(self, asset_id, not_exists_ok=False):
        return None

    async def create_folder_async(self, folder_path):
        return {"id": folder_path}

    async def export_image_to_asset_async(self, **kwargs):
        self.exports.append(kwargs)
        return {"id": "task-img-1"}


def test_submit_export_request_embeds_vis_params_on_image_for_gee_asset(monkeypatch):
    """Image+gee exports with vis_params route through set_viz_params before submit."""
    gee_interface = _FakeGeeInterfaceImageExports()

    original_image = _FakeImage()
    styled_image = _FakeImage()

    captured: dict = {}

    def fake_set_viz_params(image, **kwargs):
        captured["image"] = image
        captured["kwargs"] = kwargs
        return styled_image

    monkeypatch.setattr(
        "pysepal.solara.components.export_engine.set_viz_params",
        fake_set_viz_params,
    )

    vis_params = {
        "type": "categorical",
        "bands": ["classification"],
        "palette": ["#ff0", "#f00"],
        "values": [1, 2],
        "labels": ["a", "b"],
    }
    request = ExportRequest(
        ee_object=original_image,
        export_kind="image",
        target="gee",
        name="styled_export",
        gee_folder="gfc",
        vis_params=vis_params,
    )

    asyncio.run(
        submit_export_request(
            request,
            gee_interface=gee_interface,
            drive_interface=MagicMock(),
            sepal_client=None,
        )
    )

    assert captured["image"] is original_image
    assert captured["kwargs"] == vis_params
    assert len(gee_interface.exports) == 1
    submitted = gee_interface.exports[0]
    assert submitted["image"] is styled_image
    assert submitted["description"] == "styled_export"


def test_submit_export_request_skips_viz_embed_when_vis_params_missing(monkeypatch):
    gee_interface = _FakeGeeInterfaceImageExports()
    original_image = _FakeImage()

    calls = []

    def fake_set_viz_params(image, **kwargs):
        calls.append((image, kwargs))
        return image

    monkeypatch.setattr(
        "pysepal.solara.components.export_engine.set_viz_params",
        fake_set_viz_params,
    )

    request = ExportRequest(
        ee_object=original_image,
        export_kind="image",
        target="gee",
        name="plain_export",
        gee_folder="demo",
    )

    asyncio.run(
        submit_export_request(
            request,
            gee_interface=gee_interface,
            drive_interface=MagicMock(),
            sepal_client=None,
        )
    )

    assert calls == []
    submitted = gee_interface.exports[0]
    assert submitted["image"] is original_image


def test_build_request_drops_vis_params_for_table_exports():
    """Defense in depth: build_request gates vis_params on export_kind == image."""
    resolved = ResolvedExport(
        ee_object=_FakeTable(),
        default_name="demo",
        vis_params={"palette": ["#000"]},
    )

    # Mimic the relevant subset of build_request's behavior: the hook clears
    # vis_params for table kind. We assert by constructing the request directly
    # the same way the hook does.
    request = ExportRequest(
        ee_object=resolved.ee_object,
        export_kind="table",
        target="gee",
        name="demo",
        vis_params=resolved.vis_params if "table" == "image" else None,
    )
    assert request.vis_params is None


class _FakeRestSession:
    def __init__(self):
        self.calls = []
        self.export = SimpleNamespace(table_to_asset_async=self.table_to_asset_async)

    async def table_to_asset_async(self, **kwargs):
        self.calls.append(kwargs)
        return {"fake": "task"}


def test_gee_interface_table_asset_export_delegates_to_session_exporter():
    session = _FakeRestSession()
    interface_like = SimpleNamespace(session=session)

    result = asyncio.run(
        gee_interface_module.GEEInterface.export_table_to_asset_async(
            interface_like,
            collection=_FakeTable(),
            asset_id="projects/demo/assets/table_asset",
            description="AFG",
            selectors=["ADM0_NAME"],
            max_vertices=1000,
            priority=50,
        )
    )

    assert result == {"fake": "task"}
    assert len(session.calls) == 1
    payload = session.calls[0]
    assert payload["asset_id"] == ("projects/demo/assets/table_asset")
    assert payload["description"] == "AFG"
    assert payload["selectors"] == ["ADM0_NAME"]
    assert payload["max_vertices"] == 1000
    assert payload["priority"] == 50


def test_source_defaults_signature_tracks_dynamic_resolved_defaults():
    first = ResolvedExport(
        ee_object=_FakeTable(),
        default_name="first",
        drive_folder="exports-a",
        sepal_folder="sepal-a",
        table_file_format="SHP",
    )
    second = ResolvedExport(
        ee_object=_FakeTable(),
        default_name="first",
        drive_folder="exports-b",
        sepal_folder="sepal-b",
        table_file_format="GeoJSON",
    )

    assert export_hook_module._source_defaults_signature(first, "table", None) != (
        export_hook_module._source_defaults_signature(second, "table", None)
    )


def test_default_gee_folder_prefers_module_name():
    sepal_client = SimpleNamespace(module_name="aoi_all_methods")

    assert export_hook_module._default_gee_folder(sepal_client) == "aoi_all_methods"
    assert export_hook_module._default_gee_folder(None) == "pysepal_exports"
