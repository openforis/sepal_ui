"""Solara-compatible AOI (Area of Interest) selection component.

This module provides a Solara component for AOI selection with multiple methods including
administrative boundaries, vector files, drawn shapes, and Earth Engine assets.

Location: sepal_ui/solara/components/aoi.py

Usage:
    from sepal_ui.solara.components.aoi import AoiView

    @solara.component
    def MyApp():
        model = AoiModel()
        AoiView(model=model, methods="ALL", gee=True)
"""

from datetime import datetime as dt
from pathlib import Path
from typing import Dict, List, Optional, Union

import pygadm
import pygaul
import reacton.ipyvuetify as rv
import solara
from deprecated.sphinx import versionadded

from sepal_ui import mapping as sm
from sepal_ui.aoi.aoi_model import AoiModel
from sepal_ui.message import ms
from sepal_ui.scripts import utils as su

__all__ = ["AoiView", "MethodSelect", "AdminField"]

# Constants from AoiModel
CUSTOM = AoiModel.CUSTOM
ADMIN = AoiModel.ADMIN
ALL = "All"
select_methods = AoiModel.METHODS


@solara.component
def MethodSelect(
    methods: Union[str, List[str]] = "ALL",
    gee: bool = True,
    map_: Optional[sm.SepalMap] = None,
    value: solara.Reactive[Optional[str]] = None,
):
    """A method selector for AOI selection.

    Lists available methods for AOI selection. 'ALL' will select all available methods (default).
    'ADMIN' only the admin methods, 'CUSTOM' only the custom methods.
    Individual methods can be added (e.g., ['ADMIN0', 'SHAPE']) or removed (e.g., ['-DRAW', '-ASSET']).

    Args:
        methods: A list of methods from the available list (ADMIN0, ADMIN1, ADMIN2, SHAPE, DRAW, POINTS, ASSET)
        gee: Whether to bind to Earth Engine or not
        map_: Link the aoi_view to a custom SepalMap to display the output, default to None
        value: Reactive variable for the selected method

    Returns:
        A Solara select component for method selection
    """
    # Create the method list based on input
    if methods == "ALL":
        method_dict = select_methods
    elif methods == "ADMIN":
        method_dict = {k: v for k, v in select_methods.items() if v["type"] == ADMIN}
    elif methods == "CUSTOM":
        method_dict = {k: v for k, v in select_methods.items() if v["type"] == CUSTOM}
    elif isinstance(methods, list):
        if any(m[0] == "-" for m in methods) and not all(m[0] == "-" for m in methods):
            raise ValueError("Cannot mix adding and removing methods")

        if methods[0][0] == "-":
            to_remove = [method[1:] for method in methods]
            method_dict = {k: v for k, v in select_methods.items() if k not in to_remove}
        else:
            method_dict = {k: select_methods[k] for k in methods if k in select_methods}
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

    # Create internal state if value not provided
    internal_value = solara.use_reactive("")  # Always call hook
    active_value = value if value is not None else internal_value

    # Create the select component
    with rv.Select(
        label=ms.aoi_sel.method,
        items=items,
        v_model=active_value.value,
        dense=True,
        on_v_model=active_value.set,
    ):
        pass


@solara.component
def AdminField(
    level: int,
    parent_value: solara.Reactive[Optional[str]] = None,
    gee: bool = True,
    value: solara.Reactive[Optional[str]] = None,
):
    """An administrative level selector.

    Bound to Earth Engine (GAUL 2015) or not (GADM). Allows selection of administrative
    codes taking into account the parent administrative level.

    Args:
        level: The administrative level of the field (0, 1, or 2)
        parent_value: The reactive value of the parent admin field to filter results
        gee: Whether to use Earth Engine or not (default to True)
        value: Reactive variable for the selected admin code

    Returns:
        A Solara select component for admin code selection
    """
    # Create internal state (always call hooks)
    internal_value = solara.use_reactive(None)
    items = solara.use_reactive([])
    is_visible = solara.use_reactive(False)

    # Use provided value or internal value
    active_value = value if value is not None else internal_value

    def get_items(filter_: str = ""):
        """Update the item list based on the given filter."""
        AdmNames = pygaul.AdmNames if gee else pygadm.Names
        df = AdmNames(admin=filter_, content_level=level)
        df = df.sort_values(by=[df.columns[0]])

        # Format as item list for select component
        item_list = []
        for _, r in df.iterrows():
            text = su.normalize_str(r.iloc[0], folder=False)
            item_list.append({"text": text, "value": str(r.iloc[1])})

        items.set(item_list)

    # Effect to update items when parent changes
    def update_items():
        if parent_value is not None and parent_value.value:
            active_value.set(None)  # Reset current value
            get_items(parent_value.value)
            is_visible.set(True)
        elif parent_value is None and level == 0:
            # Level 0 has no parent, load all items
            get_items()
            is_visible.set(True)
        else:
            items.set([])
            active_value.set(None)
            is_visible.set(False)

    # Run effect when parent changes or on mount
    parent_dep = parent_value.value if parent_value is not None else None
    solara.use_effect(update_items, [parent_dep])

    # Render only if visible
    if is_visible.value:
        with rv.Select(
            label=ms.aoi_sel.adm[level],
            items=items.value,
            v_model=active_value.value,
            clearable=True,
            on_v_model=active_value.set,
        ):
            pass


@solara.component
@versionadded(version="3.0", reason="Solara-compatible AOI selection component")
def AoiView(
    model: Optional[AoiModel] = None,
    methods: Union[str, List[str]] = "ALL",
    map_: Optional[sm.SepalMap] = None,
    gee: bool = True,
    folder: Union[str, Path] = "",
    map_style: Optional[dict] = None,
):
    """Solara component for AOI (Area of Interest) selection.

    Provides multiple selection methods including administrative boundaries (GADM/GAUL),
    vector files, drawn shapes, points, and Earth Engine assets. The component is fully
    reactive and updates the provided model automatically.

    Args:
        model: The AoiModel to store the selected AOI data. If None, creates a new one
        methods: Methods to enable ('ALL', 'ADMIN', 'CUSTOM', or list of method names)
        map_: Link to a SepalMap instance for drawing and display
        gee: Whether to bind to Earth Engine
        folder: Folder name used in GEE components (for debugging)
        map_style: Custom style for AOI display on map

    Example:
        ```python
        @solara.component
        def MyApp():
            model = AoiModel()
            my_map = sm.SepalMap()

            with solara.Column():
                AoiView(model=model, map_=my_map)
                # Map will automatically update when AOI is selected
        ```
    """
    # Initialize model
    if model is None:
        model = AoiModel(gee=gee, folder=folder)

    # Initialize Earth Engine if needed
    if gee:
        su.init_ee()

    # Initialize DrawControl if map is provided
    aoi_dc = None
    if map_:
        aoi_dc = map_.dc

    # State management - all hooks must be called unconditionally
    selected_method = solara.use_reactive("")
    admin_0_value = solara.use_reactive(None)
    admin_1_value = solara.use_reactive(None)
    admin_2_value = solara.use_reactive(None)
    vector_file = solara.use_reactive(None)
    points_file = solara.use_reactive(None)
    draw_name = solara.use_reactive(None)
    asset_name = solara.use_reactive(None)

    alert_message = solara.use_reactive("")
    alert_type = solara.use_reactive("info")
    is_loading = solara.use_reactive(False)

    # Determine which methods are available
    _get_available_methods(methods, gee, map_)

    def reset_inputs():
        """Reset all input values."""
        admin_0_value.set(None)
        admin_1_value.set(None)
        admin_2_value.set(None)
        vector_file.set(None)
        points_file.set(None)
        draw_name.set(None)
        asset_name.set(None)
        alert_message.set("")

    async def process_aoi():
        """Process the selected AOI asynchronously.

        Returns:
            Success message
        """
        try:
            # Update model based on selected method
            method = selected_method.value

            if method in ["ADMIN0", "ADMIN1", "ADMIN2"]:
                # Handle administrative boundaries
                admin_code = None
                if method == "ADMIN0" and admin_0_value.value:
                    admin_code = admin_0_value.value
                elif method == "ADMIN1" and admin_1_value.value:
                    admin_code = admin_1_value.value
                elif method == "ADMIN2" and admin_2_value.value:
                    admin_code = admin_2_value.value
                else:
                    raise ValueError("Please select an administrative area")

                model.admin = admin_code
                model.method = method

                # Call async_set_object which uses AsyncItems.create() for non-GEE
                await model.async_set_object()

            elif method == "SHAPE" and vector_file.value:
                model.vector_json = vector_file.value
                model.method = method
                await model.async_set_object()

            elif method == "POINTS" and points_file.value:
                model.point_json = points_file.value
                model.method = method
                await model.async_set_object()

            elif method == "DRAW" and draw_name.value:
                model.name = draw_name.value
                # Get drawn features from DrawControl if available
                if aoi_dc:
                    model.geo_json = aoi_dc.to_json()
                else:
                    raise ValueError("No map available for drawing")

                model.method = method
                await model.async_set_object()

            elif method == "ASSET" and asset_name.value:
                model.asset_json = asset_name.value
                model.method = method
                await model.async_set_object()

            # Update the map if available
            if map_:
                map_.remove_layer("aoi", none_ok=True)
                map_.zoom_bounds(model.total_bounds())

                if gee:
                    map_.add_ee_layer(model.feature_collection, {}, "aoi")
                else:
                    map_.add_layer(model.get_ipygeojson(map_style), "aoi")

            return ms.aoi_sel.complete

        except Exception as e:
            # Clean up model state on error
            model.clear_output()
            raise e

    # Run AOI processing as async task (supports cancellation for async operations)
    # dependencies=None prevents automatic execution on mount - only runs when start_process() is called
    # raise_error=False captures errors in result.exception instead of raising them
    result = solara.lab.use_task(
        process_aoi,
        dependencies=None,
        raise_error=False,
    )

    # Update UI based on result state
    def handle_result_state():
        if result.pending:
            is_loading.set(True)
            alert_message.set("Processing AOI... This may take a moment for GADM data downloads.")
            alert_type.set("info")
        elif result.finished:
            is_loading.set(False)
            if result.value:
                alert_message.set(result.value)
                alert_type.set("success")
        elif result.error:
            is_loading.set(False)
            alert_message.set(f"Error: {str(result.exception)}")
            alert_type.set("error")
        elif result.cancelled:
            is_loading.set(False)
            alert_message.set("Process cancelled")
            alert_type.set("info")

    solara.use_effect(
        handle_result_state, [result.pending, result.finished, result.error, result.cancelled]
    )

    def start_process():
        """Trigger the background process by calling the task."""
        alert_message.set("")
        result()  # Call the task directly

    # Effect to reset inputs when method changes
    def on_method_change():
        if selected_method.value:
            reset_inputs()

            # Clear any existing AOI layer from the map
            if map_:
                map_.remove_layer("aoi", none_ok=True)

            # Handle DrawControl visibility and cleanup
            if aoi_dc:
                if selected_method.value == "DRAW":
                    aoi_dc.show()
                    now = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
                    draw_name.set(f"Manual_aoi_{now}")
                else:
                    # Hide draw control and clear any drawn features
                    aoi_dc.hide()
                    aoi_dc.clear()

    solara.use_effect(on_method_change, [selected_method.value])

    # Render the component
    with rv.Card(class_="pa-4"):
        with rv.CardTitle():
            solara.Text("AOI Selection")

        with rv.CardText():
            # Method selector
            MethodSelect(
                methods=methods,
                gee=gee,
                map_=map_,
                value=selected_method,
            )

            # Conditional rendering based on selected method
            if selected_method.value == "ADMIN0":
                AdminField(level=0, gee=gee, value=admin_0_value)

            elif selected_method.value == "ADMIN1":
                AdminField(level=0, gee=gee, value=admin_0_value)
                AdminField(level=1, parent_value=admin_0_value, gee=gee, value=admin_1_value)

            elif selected_method.value == "ADMIN2":
                AdminField(level=0, gee=gee, value=admin_0_value)
                AdminField(level=1, parent_value=admin_0_value, gee=gee, value=admin_1_value)
                AdminField(level=2, parent_value=admin_1_value, gee=gee, value=admin_2_value)

            elif selected_method.value == "SHAPE":
                solara.Info("Vector file selection - implement using VectorField component")
                # TODO: Integrate VectorField component when available in Solara

            elif selected_method.value == "POINTS":
                solara.Info("Points file selection - implement using LoadTableField component")
                # TODO: Integrate LoadTableField component when available in Solara

            elif selected_method.value == "DRAW":
                with rv.TextField(
                    label=ms.aoi_sel.aoi_name,
                    v_model=draw_name.value,
                    on_v_model=draw_name.set,
                ):
                    pass
                if map_:
                    solara.Info("Draw your AOI on the map using the draw tools")
                else:
                    solara.Warning("Map not available - DRAW method requires a map")

            elif selected_method.value == "ASSET" and gee:
                solara.Info("Earth Engine asset selection - implement using AssetSelect component")
                # TODO: Integrate AssetSelect component when available in Solara

            # Action button - changes between Process and Cancel
            if selected_method.value:
                with solara.Row():
                    solara.Button(
                        label=ms.aoi_sel.btn,
                        on_click=start_process,
                        color="primary",
                        disabled=result.pending,
                        loading=result.pending,
                    )
                    if result.pending:
                        solara.Button(
                            label="Cancel",
                            on_click=result.cancel,
                            color="error",
                            outlined=True,
                        )
            with solara.Row(classes="mt-4"):

                # Alert message
                if alert_message.value:
                    if alert_type.value == "success":
                        solara.Success(alert_message.value)
                    elif alert_type.value == "error":
                        solara.Error(alert_message.value)
                    else:
                        solara.Info(alert_message.value)


def _get_available_methods(
    methods: Union[str, List[str]],
    gee: bool,
    map_: Optional[sm.SepalMap],
) -> Dict[str, Dict[str, str]]:
    """Helper function to determine available methods based on configuration.

    Args:
        methods: Methods configuration
        gee: Whether Earth Engine is available
        map_: Map instance

    Returns:
        Dictionary of available methods
    """
    # Create the method list
    if methods == "ALL":
        method_dict = select_methods.copy()
    elif methods == "ADMIN":
        method_dict = {k: v for k, v in select_methods.items() if v["type"] == ADMIN}
    elif methods == "CUSTOM":
        method_dict = {k: v for k, v in select_methods.items() if v["type"] == CUSTOM}
    elif isinstance(methods, list):
        if any(m[0] == "-" for m in methods) and not all(m[0] == "-" for m in methods):
            raise ValueError("Cannot mix adding and removing methods")

        if methods[0][0] == "-":
            to_remove = [method[1:] for method in methods]
            method_dict = {k: v for k, v in select_methods.items() if k not in to_remove}
        else:
            method_dict = {k: select_methods[k] for k in methods if k in select_methods}
    else:
        method_dict = select_methods.copy()

    # Clean the list based on availability
    if not gee:
        method_dict.pop("ASSET", None)
    if map_ is None:
        method_dict.pop("DRAW", None)

    return method_dict
