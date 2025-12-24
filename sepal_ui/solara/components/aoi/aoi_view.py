"""Solara-native AOI (Area of Interest) selection component.

This module provides pure Solara components for AOI selection following modern
Solara patterns with value/on_value parameters.

Usage:
    from sepal_ui.solara.components.aoi import AoiView, AoiResult

    @solara.component
    def MyApp():
        aoi = solara.use_reactive(None)

        AoiView(
            value=aoi,
            methods="ALL",
            gee=True
        )

        # Access AOI data when available
        if aoi.value:
            print(f"Selected: {aoi.value.name}")
"""

from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

import reacton.ipyvuetify as rv
import solara
from deprecated.sphinx import versionadded

from sepal_ui import mapping as sm
from sepal_ui.message import ms
from sepal_ui.scripts import utils as su
from sepal_ui.solara.components.aoi.admin import (
    fetch_admin_bounds_async,
    fetch_admin_items,
    process_admin,
)
from sepal_ui.solara.components.aoi.aoi_result import AoiResult
from sepal_ui.solara.components.aoi.draw import process_draw
from sepal_ui.solara.components.aoi.wms_utils import (
    WMS_PREVIEW_LAYER_NAME,
    create_wms_preview_layer,
)

__all__ = ["AoiView", "MethodSelect", "AdminLevelSelector", "AoiResult"]

# Method type constants
CUSTOM: str = ms.aoi_sel.custom
ADMIN: str = ms.aoi_sel.administrative

# Available selection methods
METHODS: Dict[str, Dict[str, str]] = {
    "ADMIN0": {"name": ms.aoi_sel.adm[0], "type": ADMIN},
    "ADMIN1": {"name": ms.aoi_sel.adm[1], "type": ADMIN},
    "ADMIN2": {"name": ms.aoi_sel.adm[2], "type": ADMIN},
    "SHAPE": {"name": ms.aoi_sel.vector, "type": CUSTOM},
    "DRAW": {"name": ms.aoi_sel.draw, "type": CUSTOM},
    "POINTS": {"name": ms.aoi_sel.points, "type": CUSTOM},
    "ASSET": {"name": ms.aoi_sel.asset, "type": CUSTOM},
}


@solara.component
def MethodSelect(
    methods: Union[str, List[str]] = "ALL",
    gee: bool = True,
    map_: Optional[sm.SepalMap] = None,
    value: Union[str, solara.Reactive[str]] = "",
    on_value: Optional[Callable[[str], None]] = None,
):
    """A method selector for AOI selection.

    Lists available methods for AOI selection. 'ALL' will select all available methods.
    'ADMIN' only the admin methods, 'CUSTOM' only the custom methods.
    Individual methods can be added (e.g., ['ADMIN0', 'SHAPE']) or removed (e.g., ['-DRAW', '-ASSET']).

    Args:
        methods: A list of methods from the available list
        gee: Whether to bind to Earth Engine or not
        map_: Link the aoi_view to a custom SepalMap to display the output
        value: Current selected method (can be reactive)
        on_value: Callback when method changes

    Returns:
        None
    """
    reactive_value = solara.use_reactive(value, on_value)
    del value, on_value

    # Create the method list based on input
    if methods == "ALL":
        method_dict = METHODS.copy()
    elif methods == "ADMIN":
        method_dict = {k: v for k, v in METHODS.items() if v["type"] == ADMIN}
    elif methods == "CUSTOM":
        method_dict = {k: v for k, v in METHODS.items() if v["type"] == CUSTOM}
    elif isinstance(methods, list):
        if any(m[0] == "-" for m in methods) and not all(m[0] == "-" for m in methods):
            raise ValueError("Cannot mix adding and removing methods")

        if methods[0][0] == "-":
            to_remove = [method[1:] for method in methods]
            method_dict = {k: v for k, v in METHODS.items() if k not in to_remove}
        else:
            method_dict = {k: METHODS[k] for k in methods if k in METHODS}
    else:
        raise ValueError("Invalid methods parameter")

    # Clean the list from things we can't use
    if not gee:
        method_dict.pop("ASSET", None)
    if map_ is None:
        method_dict.pop("DRAW", None)

    # Build the item list with headers
    prev_type = None
    items = []
    for k, m in method_dict.items():
        current_type = m["type"]

        if prev_type != current_type:
            items.append({"header": current_type})
        prev_type = current_type

        items.append({"text": m["name"], "value": k})

    with rv.Select(
        label=ms.aoi_sel.method,
        items=items,
        v_model=reactive_value.value,
        dense=True,
        on_v_model=reactive_value.set,
    ):
        pass


@solara.component
@versionadded(version="3.1", reason="Self-contained admin level selector")
def AdminLevelSelector(
    method: str,
    gee: bool = True,
    map_: Optional[sm.SepalMap] = None,
    value: Union[str, solara.Reactive[Optional[str]]] = None,
    on_value: Optional[Callable[[Optional[str]], None]] = None,
):
    """Self-contained administrative level selector with cascading dropdowns.

    Manages internal state for cascading admin levels (0, 1, 2) and exposes
    only the final selected admin code. Provides a stable render tree regardless
    of the method (ADMIN0, ADMIN1, ADMIN2).

    When a map is provided and gee=False, shows a WMS preview of the selected
    admin boundary on the map immediately after selection.

    Args:
        method: The admin method ("ADMIN0", "ADMIN1", or "ADMIN2")
        gee: Whether to use Earth Engine (GAUL) or FAO WFS (local)
        map_: Optional SepalMap to display WMS preview (only for gee=False)
        value: The final selected admin code (output only)
        on_value: Callback when the final admin code changes

    Returns:
        None. The final admin code is passed through value/on_value.

    Example:
        ```python
        @solara.component
        def MyApp():
            admin_code = solara.use_reactive(None)
            my_map = sm.SepalMap()

            AdminLevelSelector(
                method="ADMIN1",
                gee=False,
                map_=my_map,
                value=admin_code,
            )

            if admin_code.value:
                solara.Text(f"Selected: {admin_code.value}")
        ```
    """
    reactive_value = solara.use_reactive(value, on_value)
    del value, on_value

    # Internal state for each level - ALWAYS created (stable hooks)
    level_0 = solara.use_reactive(None)
    level_1 = solara.use_reactive(None)
    level_2 = solara.use_reactive(None)

    # Items for each level
    items_0 = solara.use_reactive([])
    items_1 = solara.use_reactive([])
    items_2 = solara.use_reactive([])

    # Loading states for async fetches
    loading_0 = solara.use_reactive(False)
    loading_1 = solara.use_reactive(False)
    loading_2 = solara.use_reactive(False)

    # Determine target level from method
    target_level = {"ADMIN0": 0, "ADMIN1": 1, "ADMIN2": 2}.get(method, 0)

    # Async task to load level 0 items
    async def _load_level_0():
        loading_0.set(True)
        try:
            items = fetch_admin_items(level=0, parent_code="")
            items_0.set(items)
        finally:
            loading_0.set(False)

    solara.lab.use_task(_load_level_0, dependencies=[], raise_error=False)

    # Async task to load level 1 items
    async def _load_level_1():
        if level_0.value and target_level >= 1:
            loading_1.set(True)
            try:
                items = fetch_admin_items(level=1, parent_code=level_0.value)
                items_1.set(items)
            finally:
                loading_1.set(False)
        else:
            items_1.set([])
        # Reset downstream
        level_1.set(None)
        level_2.set(None)
        items_2.set([])

    solara.lab.use_task(
        _load_level_1,
        dependencies=[level_0.value, target_level],
        raise_error=False,
    )

    # Async task to load level 2 items
    async def _load_level_2():
        if level_1.value and target_level >= 2:
            loading_2.set(True)
            try:
                items = fetch_admin_items(level=2, parent_code=level_1.value)
                items_2.set(items)
            finally:
                loading_2.set(False)
        else:
            items_2.set([])
        # Reset downstream
        level_2.set(None)

    solara.lab.use_task(
        _load_level_2,
        dependencies=[level_1.value, target_level],
        raise_error=False,
    )

    # Update output value when target level selection changes
    def update_output():
        if target_level == 0:
            reactive_value.set(level_0.value)
        elif target_level == 1:
            reactive_value.set(level_1.value)
        elif target_level == 2:
            reactive_value.set(level_2.value)

    solara.use_effect(update_output, [level_0.value, level_1.value, level_2.value, target_level])

    # Render - stable structure, control visibility
    with solara.Column(classes="pa-0 ma-0", style="gap: 8px;"):
        # Level 0 - always visible for admin methods
        with rv.Select(
            label=ms.aoi_sel.adm[0],
            items=items_0.value,
            v_model=level_0.value,
            clearable=True,
            dense=True,
            loading=loading_0.value,
            on_v_model=level_0.set,
        ):
            pass

        # Level 1 - visible for ADMIN1 and ADMIN2
        if target_level >= 1:
            with rv.Select(
                label=ms.aoi_sel.adm[1],
                items=items_1.value,
                v_model=level_1.value,
                clearable=True,
                dense=True,
                loading=loading_1.value,
                disabled=not level_0.value,
                on_v_model=level_1.set,
            ):
                pass

        # Level 2 - visible only for ADMIN2
        if target_level >= 2:
            with rv.Select(
                label=ms.aoi_sel.adm[2],
                items=items_2.value,
                v_model=level_2.value,
                clearable=True,
                dense=True,
                loading=loading_2.value,
                disabled=not level_1.value,
                on_v_model=level_2.set,
            ):
                pass


@solara.component
@versionadded(version="3.1", reason="Pure Solara AOI selection component")
def AoiView(
    value: Union[AoiResult, solara.Reactive[Optional[AoiResult]]] = None,
    on_value: Optional[Callable[[Optional[AoiResult]], None]] = None,
    loading: Union[bool, solara.Reactive[bool]] = False,
    on_loading: Optional[Callable[[bool], None]] = None,
    methods: Union[str, List[str]] = "ALL",
    map_: Optional[sm.SepalMap] = None,
    gee: bool = True,
    folder: Union[str, Path] = "",
    map_style: Optional[dict] = None,
):
    """Solara-native component for AOI (Area of Interest) selection.

    Provides multiple selection methods including administrative boundaries (GADM/GAUL),
    vector files, drawn shapes, points, and Earth Engine assets. The component follows
    modern Solara patterns with value/on_value for reactive data flow.

    Args:
        value: AoiResult containing AOI data. Can be reactive.
        on_value: Callback function called when AOI is selected/updated
        loading: Whether the component is in loading state
        on_loading: Callback when loading state changes
        methods: Methods to enable ('ALL', 'ADMIN', 'CUSTOM', or list of method names)
        map_: Link to a SepalMap instance for drawing and display
        gee: Whether to bind to Earth Engine
        folder: Folder name used in GEE components
        map_style: Custom style for AOI display on map

    Example:
        ```python
        @solara.component
        def MyApp():
            aoi = solara.use_reactive(None)
            my_map = sm.SepalMap()

            with solara.Column():
                AoiView(value=aoi, map_=my_map, gee=False)

                if aoi.value:
                    solara.Success(f"Selected: {aoi.value.name}")
        ```

    Returns:
        None. AOI data is passed through value/on_value as AoiResult.
    """
    # Normalize value/loading to reactive
    reactive_value = solara.use_reactive(value, on_value)
    reactive_loading = solara.use_reactive(loading, on_loading)
    del value, on_value, loading, on_loading

    # Validate GEE consistency between map and AoiView
    if map_ is not None and hasattr(map_, "gee"):
        if map_.gee != gee:
            raise ValueError(
                f"GEE setting mismatch: AoiView has gee={gee} but map has gee={map_.gee}. "
                f"Both must have the same GEE setting for proper functionality."
            )

    # Initialize Earth Engine once
    def _ensure_ee():
        if gee:
            su.init_ee()
        return None

    solara.use_effect(_ensure_ee, [gee])

    # Get DrawControl if map is provided
    aoi_dc = map_.dc if map_ else None

    # State management - minimal state in AoiView
    selected_method = solara.use_reactive("")
    admin_code = solara.use_reactive(None)  # Output from AdminLevelSelector
    draw_name = solara.use_reactive("")  # Name for drawn shapes

    # UI state
    alert_message = solara.use_reactive("")
    alert_type = solara.use_reactive("info")

    # Reset alert on mount
    def reset_alert_on_mount():
        alert_message.set("")
        alert_type.set("info")

    solara.use_effect(reset_alert_on_mount, [])  # Empty deps = runs once on mount

    async def process_aoi() -> str:
        """Process the selected AOI."""
        method = selected_method.value

        if method in ["ADMIN0", "ADMIN1", "ADMIN2"]:
            if not admin_code.value:
                raise ValueError(f"Please select a {method} region")

            result = await process_admin(
                method=method,
                admin_code=admin_code.value,
                gee=gee,
            )

        elif method == "DRAW":
            if aoi_dc is None:
                raise ValueError("No DrawControl available")

            features = aoi_dc.get_data()
            if not features:
                raise ValueError("No drawn features found. Please draw an area on the map.")

            result = process_draw(
                geo_json=features,
                name=draw_name.value,
                gee=gee,
                folder=folder,
            )

        elif method == "SHAPE":
            raise NotImplementedError("SHAPE method not yet implemented")

        elif method == "POINTS":
            raise NotImplementedError("POINTS method not yet implemented")

        elif method == "ASSET":
            raise NotImplementedError("ASSET method not yet implemented")

        else:
            raise ValueError("Please select a method")

        # Update the map if available
        if map_ and result:
            # Clear existing AOI layers and WMS preview
            for layer in list(map_.layers):
                if hasattr(layer, "name") and layer.name in ["aoi", WMS_PREVIEW_LAYER_NAME]:
                    map_.remove_layer(layer)

            # Add new AOI layer
            if gee and result.feature_collection:
                await map_.add_ee_layer_async(
                    result.feature_collection, map_style or {}, "aoi", autocenter=True
                )
            elif result.admin is not None:
                # For admin boundaries (non-GEE), use WMS layer and zoom to bounds
                level = int(method[-1])  # Extract level from method name (ADMIN0 -> 0)
                wms_layer = create_wms_preview_layer(
                    level=level,
                    admin_code=result.admin,
                    name="aoi",
                )
                map_.add_layer(wms_layer)

                # Fetch bounds async and zoom to the feature
                bounds = await fetch_admin_bounds_async(level=level, admin_code=result.admin)
                map_.zoom_bounds(bounds)
            elif result.gdf is not None:
                # For drawn shapes or other methods with GDF, use GeoJSON
                from sepal_ui.mapping import get_ipygeojson

                geojson_layer = get_ipygeojson(result.gdf, result.name, map_style)
                map_.add_layer(geojson_layer, "aoi")

                # Zoom to the GeoDataFrame bounds
                map_.zoom_bounds(result.gdf.total_bounds)

        # Update reactive value
        reactive_value.set(result)

        return ms.aoi_sel.complete

    # Run AOI processing as async task
    task = solara.lab.use_task(
        process_aoi,
        dependencies=None,
        raise_error=False,
    )

    # Handle task state changes
    def handle_task_state():
        if task.pending:
            reactive_loading.set(True)
            alert_message.set("Processing AOI...")
            alert_type.set("info")
        elif task.finished:
            reactive_loading.set(False)
            if task.value:
                alert_message.set(task.value)
                alert_type.set("success")
        elif task.error:
            reactive_loading.set(False)
            alert_message.set(f"Error: {str(task.exception)}")
            alert_type.set("error")
        elif task.cancelled:
            reactive_loading.set(False)
            alert_message.set("Process cancelled")
            alert_type.set("info")

    solara.use_effect(handle_task_state, [task.pending, task.finished, task.error, task.cancelled])

    def start_process():
        """Trigger the background process."""
        alert_message.set("")
        reactive_loading.set(True)
        task()

    # Handle method changes
    def on_method_change():
        if selected_method.value:
            # Clear previous AOI
            reactive_value.set(None)
            admin_code.set(None)
            draw_name.set("")
            alert_message.set("")

            # Clear AOI layer and WMS preview from map
            if map_:
                for layer in list(map_.layers):
                    if hasattr(layer, "name") and layer.name in ["aoi", WMS_PREVIEW_LAYER_NAME]:
                        map_.remove_layer(layer)

            # Handle DrawControl
            if aoi_dc:
                if selected_method.value == "DRAW":
                    aoi_dc.clear()
                    if aoi_dc not in map_.controls:
                        map_.add_control(aoi_dc)
                else:
                    if aoi_dc in map_.controls:
                        map_.remove_control(aoi_dc)

    solara.use_effect(on_method_change, [selected_method.value])

    # Cleanup on unmount
    def _cleanup():
        def cleanup():
            # Note: We don't cancel the task here because task.cancel() raises
            # _CancelledErrorInOurTask which propagates up. The task will be
            # garbage collected when the component unmounts.

            reactive_loading.set(False)
            alert_message.set("")

            if map_:
                try:
                    for layer in list(map_.layers):
                        if hasattr(layer, "name") and layer.name in ["aoi", WMS_PREVIEW_LAYER_NAME]:
                            map_.remove_layer(layer)
                except Exception:
                    pass

                if aoi_dc:
                    try:
                        aoi_dc.clear()
                        if aoi_dc in map_.controls:
                            map_.remove_control(aoi_dc)
                    except Exception:
                        pass

                # Reset map to default center (Bogota) and zoom
                try:
                    map_.center = (4.6097, -74.0817)  # Bogota, Colombia
                    map_.zoom = 10
                except Exception:
                    pass

        return cleanup

    solara.use_effect(_cleanup, [id(map_) if map_ else None])

    # Render
    with solara.Column(classes="mx-0 px-0"):
        # Method selector
        MethodSelect(
            methods=methods,
            gee=gee,
            map_=map_,
            value=selected_method,
        )

        # Method-specific inputs
        if selected_method.value in ["ADMIN0", "ADMIN1", "ADMIN2"]:
            AdminLevelSelector(
                method=selected_method.value,
                gee=gee,
                map_=map_,
                value=admin_code,
            )

        elif selected_method.value == "SHAPE":
            solara.Warning("SHAPE method not yet implemented.")

        elif selected_method.value == "POINTS":
            solara.Warning("POINTS method not yet implemented.")

        elif selected_method.value == "DRAW":
            if aoi_dc:
                solara.Info("Use the drawing tools on the map to create your AOI.")
                with rv.TextField(
                    label="AOI Name (optional)",
                    v_model=draw_name.value,
                    on_v_model=draw_name.set,
                    outlined=True,
                    dense=True,
                ):
                    pass
            else:
                solara.Error("DrawControl not available. Please provide a map with DrawControl.")

        elif selected_method.value == "ASSET" and gee:
            solara.Warning("ASSET method not yet implemented.")

        # Action buttons
        if selected_method.value:
            is_loading = reactive_loading.value or task.pending
            with solara.Column():
                solara.Button(
                    "Select AOI",
                    on_click=start_process,
                    disabled=is_loading,
                    loading=is_loading,
                    color="primary",
                    block=True,
                    small=True,
                )
                if is_loading:
                    solara.Button(
                        "Cancel",
                        on_click=task.cancel,
                        color="error",
                        outlined=True,
                        block=True,
                        small=True,
                    )

        # Alert display
        if alert_message.value:
            if alert_type.value == "success":
                solara.Success(alert_message.value)
            elif alert_type.value == "error":
                solara.Error(alert_message.value)
            elif alert_type.value == "warning":
                solara.Warning(alert_message.value)
            else:
                solara.Info(alert_message.value)
