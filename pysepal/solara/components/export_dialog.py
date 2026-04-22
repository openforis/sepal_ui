"""Modal UI for the Solara export launcher."""

from __future__ import annotations

import reacton.ipyvuetify as rv
import reacton.ipyvuetify as v
import solara

from pysepal.solara.components.task_button import TaskButtonComponent, use_task_button

from .export_hook import (
    ExportDialogController,
    get_controller_source_state,
    get_source_items,
    get_target_items,
)
from .export_models import (
    TABLE_FILE_FORMATS,
    resolve_asset_folder,
    sanitize_export_name,
)

IMAGE_SCALE_PRESETS = [10, 15, 20, 30, 60, 100]


def _hint_props(hint: str) -> dict[str, object]:
    """Attach a real persistent hint only when the field needs one."""
    return {
        "hide_details": False,
        "hint": hint,
        "persistent_hint": True,
    }


def _build_gee_asset_hint(asset_root: str, requested_folder: str, export_name: str) -> str:
    """Return a humane preview of the resolved Earth Engine asset path."""
    resolved_folder = resolve_asset_folder(asset_root, requested_folder)
    asset_name = sanitize_export_name(export_name) if export_name.strip() else "<name>"
    return f"Will be exported as: {resolved_folder}/{asset_name}"


@solara.component
def InlineExportFeedback(message: str, level: str) -> None:
    """Render fallback inline feedback when notifications are unavailable."""
    if not message:
        return

    if level == "success":
        solara.Success(message)
    elif level == "error":
        solara.Error(message)
    elif level == "warning":
        solara.Warning(message)
    else:
        solara.Info(message)


@solara.component
def ImageScaleField(scale: solara.Reactive[int]) -> None:
    """Render SEPAL-style scale presets plus a custom numeric field."""
    preset_value = scale.value if scale.value in IMAGE_SCALE_PRESETS else None

    def _handle_preset_scale(value: int | None) -> None:
        if value is not None:
            scale.set(int(value))

    def _handle_custom_scale(value: str) -> None:
        try:
            numeric_value = int(float(value))
        except (TypeError, ValueError):
            return

        if numeric_value > 0:
            scale.set(numeric_value)

    with rv.Html(
        tag="div",
        style_=(
            "display: flex; align-items: center; gap: 12px;" " flex-wrap: nowrap; width: 100%;"
        ),
    ):
        solara.Text("Scale")
        with solara.ToggleButtonsSingle(
            value=preset_value,
            on_value=_handle_preset_scale,
            mandatory=False,
            dense=True,
            style={"width": "fit-content"},
        ):
            for preset in IMAGE_SCALE_PRESETS:
                solara.Button(
                    label=str(preset),
                    value=preset,
                    small=True,
                    text=True,
                )

        with rv.TextField(
            v_model=str(scale.value),
            on_v_model=_handle_custom_scale,
            type="number",
            suffix="m",
            dense=True,
            hide_details=True,
            placeholder="Custom",
            style_="max-width: 128px;",
        ):
            pass


@solara.component
def ExportDialog(
    controller: ExportDialogController,
    title: str = "Export",
    max_width: str = "720px",
):
    """Render the export dialog using an existing controller."""
    state = controller._state
    active_source, resolved_export, export_kind, resolve_error = get_controller_source_state(
        controller
    )
    has_usable_sources = any(not source.disabled for source in controller.sources)
    fields_disabled = active_source is None
    name_error = "" if fields_disabled or controller.export_name.value.strip() else "Name required"
    submit_disabled = (
        not has_usable_sources
        or active_source is None
        or resolved_export is None
        or export_kind is None
        or bool(resolve_error)
        or bool(name_error)
    )

    target_items = get_target_items(state.sepal_client)
    source_items = get_source_items(controller.sources)
    button_props = use_task_button(
        controller.task,
        on_start=controller.submit_export,
        cancel_reason_ref=state.cancel_reason_ref,
    )

    def _handle_name_change(value: str) -> None:
        controller.export_name.set(value)
        if not controller.name_dirty.value and value != state.last_default_name.value:
            controller.name_dirty.set(True)

    with v.Dialog(
        v_model=controller.open.value,
        on_v_model=controller.open.set,
        max_width=max_width,
        scrollable=True,
    ):
        with solara.v.Card():
            solara.v.CardTitle(children=[title])

            with solara.v.CardText():
                with solara.Column(style="gap: 22px; padding-top: 8px;"):
                    if not has_usable_sources:
                        solara.Warning("No exportable layers available.")
                    elif resolve_error and state.notifications_enabled:
                        solara.Warning("The selected layer cannot currently be exported.")

                    if source_items:
                        with rv.Select(
                            label="Asset",
                            items=source_items,
                            v_model=controller.selected_source_id.value,
                            on_v_model=controller.selected_source_id.set,
                            dense=True,
                            placeholder="Select asset",
                            hide_details=True,
                        ):
                            pass

                    with rv.RadioGroup(
                        label="Destination",
                        v_model=controller.selected_target.value,
                        on_v_model=controller.selected_target.set,
                        dense=True,
                        mandatory=True,
                        row=True,
                        hide_details=True,
                        disabled=fields_disabled,
                    ):
                        for item in target_items:
                            rv.Radio(
                                label=item["text"],
                                value=item["value"],
                                disabled=bool(item.get("disabled", False)) or fields_disabled,
                            )

                    with rv.TextField(
                        label="Export name",
                        v_model=controller.export_name.value,
                        on_v_model=_handle_name_change,
                        dense=True,
                        error=bool(name_error),
                        error_messages=name_error or None,
                        hide_details="auto",
                        disabled=fields_disabled,
                    ):
                        pass

                    if controller.selected_target.value == "gee":
                        asset_root_placeholder = state.asset_root.value
                        gee_asset_hint = _build_gee_asset_hint(
                            state.asset_root.value,
                            state.gee_folder.value,
                            controller.export_name.value,
                        )
                        with rv.TextField(
                            label="Earth Engine folder",
                            v_model=state.gee_folder.value,
                            on_v_model=state.gee_folder.set,
                            dense=True,
                            placeholder=asset_root_placeholder,
                            disabled=fields_disabled,
                            **_hint_props(gee_asset_hint),
                        ):
                            pass

                    if controller.selected_target.value in {"drive", "sepal"}:
                        with rv.TextField(
                            label="Google Drive folder",
                            v_model=state.drive_folder.value,
                            on_v_model=state.drive_folder.set,
                            dense=True,
                            placeholder="Drive root",
                            hide_details=True,
                            disabled=fields_disabled,
                        ):
                            pass

                    if export_kind == "image":
                        ImageScaleField(scale=state.scale)

                    if export_kind == "table" and controller.selected_target.value in {
                        "drive",
                        "sepal",
                    }:
                        with rv.Select(
                            label="Table file format",
                            items=TABLE_FILE_FORMATS,
                            v_model=state.table_file_format.value,
                            on_v_model=state.table_file_format.set,
                            dense=True,
                            hide_details=True,
                            disabled=fields_disabled,
                        ):
                            pass

                    if controller.selected_target.value == "sepal":
                        with rv.TextField(
                            label="SEPAL folder",
                            v_model=state.sepal_folder.value,
                            on_v_model=state.sepal_folder.set,
                            dense=True,
                            disabled=fields_disabled,
                            **_hint_props("Relative to the module results directory."),
                        ):
                            pass
                        solara.Info(
                            "SEPAL exports are staged through Google Drive " "before being copied."
                        )

                    if not state.notifications_enabled and state.inline_message.value:
                        InlineExportFeedback(
                            message=state.inline_message.value,
                            level=state.inline_level.value,
                        )

            with solara.v.CardActions():
                solara.v.Spacer()
                solara.Button(
                    label="Close",
                    on_click=controller.close_dialog,
                    text=True,
                    disabled=controller.task.pending,
                    small=True,
                )
                TaskButtonComponent(
                    label="Export",
                    cancel_label="Cancel",
                    **button_props,
                    external_busy=submit_disabled,
                    min_width="120px",
                    small=True,
                )


__all__ = ["ExportDialog", "InlineExportFeedback"]
