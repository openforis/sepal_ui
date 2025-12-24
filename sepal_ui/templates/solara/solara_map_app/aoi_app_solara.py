"""AOI Selection Application Template - Solara-Native Pattern.

This example demonstrates the modern Solara-native AoiView component with value/on_value
parameters following the patterns from guides/2_creating_solara_apps.md.


to run this


```bash

sepal_ui$ ./run_solara.sh sepal_ui/templates/solara/solara_map_app/aoi_app_solara.py --port 8900

```
"""

import solara

from sepal_ui import mapping as sm
from sepal_ui.solara import (
    setup_sessions,
    setup_solara_server,
    setup_theme_colors,
)
from sepal_ui.solara.components.aoi import AoiResult, AoiView
from sepal_ui.solara.components.notifications import (
    NotificationsHost,
    error,
    info,
    log,
    success,
    warning,
)

setup_solara_server(extra_asset_locations=[])


@solara.lab.on_kernel_start
def on_kernel_start():
    """Set up sessions management for Solara applications."""
    return setup_sessions()


@solara.component
def AoiWithGEE():
    """AOI selection with Google Earth Engine (GAUL boundaries).

    Demonstrates the modern Solara pattern with value/on_value for reactive data flow.
    """
    # Create reactive state for AOI data
    aoi_data = solara.use_reactive(None)
    aoi_loading = solara.use_reactive(False)
    # Use memo to prevent map reinitialization on every render
    gee_flag = True
    sepal_map = solara.use_memo(
        lambda: sm.SepalMap(zoom=2, center=[0, 0], gee=gee_flag),
        [gee_flag],
    )

    # Layout
    with solara.Column(style="padding: 20px; gap: 20px;"):
        # Header
        solara.Markdown("# AOI Selection Example (Solara-Native)")
        solara.Markdown(
            "Select an Area of Interest using the modern value/on_value pattern. "
            "No more model.observe() required!"
        )

        # Keep a stable element in the tree so AoiView isn't remounted
        # when aoi_data.value flips between None and a dict.

        # Two-column layout
        with solara.Columns([1, 1], style="gap: 20px;"):
            with solara.Column():
                AoiView(
                    value=aoi_data,  # Reactive value - automatically updates
                    loading=aoi_loading,
                    methods="ALL",  # Enable all available methods
                    map_=sepal_map,
                    gee=True,
                )

            # Right column: Map display
            with solara.Card("Map View", style="height: 100%; width: 600px;"):
                solara.display(sepal_map)


@solara.component
def AoiWithoutGEE():
    """AOI selection without Google Earth Engine (GADM boundaries).

    Demonstrates the modern Solara pattern with GADM administrative boundaries.
    """
    # Create reactive state
    aoi_data = solara.use_reactive(None)
    aoi_loading = solara.use_reactive(False)
    solara.use_reactive(True)
    solara.use_reactive(1)
    # Use memo to prevent map reinitialization on every render
    gee_flag = False
    sepal_map = solara.use_memo(
        lambda: sm.SepalMap(zoom=2, center=[0, 0], gee=gee_flag),
        [gee_flag],
    )

    # Derived state for display
    solara.use_memo(
        lambda: _format_aoi_info_gadm(aoi_data.value) if aoi_data.value else "",
        [aoi_data.value],
    )

    # Layout
    with solara.Column(style="padding: 20px; gap: 20px;"):
        # Header
        solara.Markdown("## Without Earth Engine (GADM)")
        solara.Markdown(
            "Select administrative boundaries using GADM data. "
            "Pure Solara reactive pattern - no observers needed!"
        )

        with solara.Columns([1, 1], style="gap: 20px;"):
            # AOI selection
            with solara.Column():
                AoiView(
                    value=aoi_data,  # Reactive - automatically syncs
                    loading=aoi_loading,
                    methods="ADMIN",  # Only administrative boundaries
                    map_=sepal_map,
                    gee=False,  # Use GADM instead of GAUL
                )

            # Map display
            with solara.Card("Map View"):
                solara.display(sepal_map)

        # Display AOI details - reactively appears when aoi_data has value
        if aoi_data.value:
            gdf = aoi_data.value.gdf
            if gdf is not None and not gdf.empty:
                with solara.Card("AOI Details"):
                    with solara.Column():
                        solara.Markdown(f"**Selected Method:** {aoi_data.value.method}")
                        if aoi_data.value.admin:
                            solara.Markdown(f"**Admin Code:** {aoi_data.value.admin}")
                        solara.Markdown(f"**Features:** {len(gdf)}")

                        # Show first feature properties
                        solara.Markdown("**Properties:**")
                        for col in gdf.columns[:5]:  # First 5 columns
                            if col != "geometry":
                                val = str(gdf[col].iloc[0])[:50]  # Truncate long values
                                solara.Markdown(f"- {col}: {val}")

                        # Action button
                        solara.Button(
                            "Clear AOI",
                            on_click=lambda: aoi_data.set(None),
                            color="error",
                            outlined=True,
                        )


@solara.component
def ComparisonExample():
    """Side-by-side comparison of the value/on_value pattern."""
    aoi_data = solara.use_reactive(None)

    with solara.Column(style="padding: 20px; gap: 20px;"):
        solara.Markdown("## Solara Pattern: value/on_value")
        solara.Markdown(
            """
            This example demonstrates the clean Solara pattern:
            
            ```python
            # Create reactive state
            aoi_data = solara.use_reactive(None)
            
            # Pass to component - automatically syncs!
            AoiView(value=aoi_data, methods="ALL", gee=True)
            
            # Use the data - no observers needed
            if aoi_data.value:
                area = aoi_data.value.area
                gdf = aoi_data.value.gdf
            ```
            
            **Key Benefits:**
            - No `model.observe()` needed
            - Pure reactive data flow
            - Follows Solara conventions
            - Cleaner, more maintainable code
            """
        )

        if aoi_data.value:
            solara.Success(f"✓ AOI selected: {aoi_data.value.method}")

            # Display useful information
            with solara.Card("Accessible Data"):
                solara.Markdown("**Available in aoi_data.value (AoiResult):**")
                solara.Markdown(f"- `method`: {aoi_data.value.method}")
                solara.Markdown(f"- `name`: {aoi_data.value.name}")
                solara.Markdown(f"- `area`: {aoi_data.value.area}")
                solara.Markdown(f"- `bounds`: {aoi_data.value.bounds}")
                solara.Markdown(f"- `admin`: {aoi_data.value.admin}")
                solara.Markdown(f"- `gee`: {aoi_data.value.gee}")


def _format_aoi_info(aoi_data: AoiResult) -> str:
    """Helper to format AOI info for display."""
    if not aoi_data:
        return ""

    method = aoi_data.method or "Unknown"
    area = None

    if area:
        return f"**Method:** {method} | **Area:** {area:.2f} ha"
    return f"**Method:** {method}"


def _format_aoi_info_gadm(aoi_data: AoiResult) -> str:
    """Helper to format GADM AOI info for display."""
    if not aoi_data:
        return ""

    gdf = aoi_data.gdf
    method = aoi_data.method or "Unknown"

    if gdf is not None and not gdf.empty:
        area_km2 = gdf.geometry.area.sum() / 1e6  # Approximate area in km²
        return f"**Method:** {method} | **Features:** {len(gdf)} | **Approx. Area:** {area_km2:.2f} km²"
    return f"**Method:** {method}"


@solara.component
# @with_sepal_sessions(module_name="aoi_example")  # Commented out for local testing
def Page():
    """Main AOI selection application page with modern Solara patterns."""
    setup_theme_colors()

    # Tab selection state
    selected_tab = solara.use_reactive(0)

    with solara.Column(style="padding: 20px; gap: 20px;"):
        # Notifications Host - mount once at the top of your app
        NotificationsHost(
            floating_button_position="bottom-right",
            toast_timeout_ms=4000,
        )

        # Header
        solara.Markdown("# AOI Selection - Solara-Native Pattern")
        solara.Markdown("Modern value/on_value pattern following guides/2_creating_solara_apps.md")

        # Notification Demo Section
        with solara.Card("🔔 Notification Demo", elevation=1):
            solara.Markdown(
                "Test the floating notification system. Click the bell icon "
                "in the bottom-right corner to see notification history."
            )
            with solara.Row(style="gap: 8px; flex-wrap: wrap;"):
                solara.Button(
                    "Success",
                    on_click=lambda: success("Operation completed successfully!", title="Success"),
                    color="success",
                    outlined=True,
                )
                solara.Button(
                    "Info",
                    on_click=lambda: info("Here is some useful information.", title="Info"),
                    color="info",
                    outlined=True,
                )
                solara.Button(
                    "Warning",
                    on_click=lambda: warning("Please check your configuration.", title="Warning"),
                    color="warning",
                    outlined=True,
                )
                solara.Button(
                    "Error",
                    on_click=lambda: error("Something went wrong!", title="Error"),
                    color="error",
                    outlined=True,
                )
                solara.Button(
                    "Log (no toast)",
                    on_click=lambda: log("Background process completed", title="System"),
                    outlined=True,
                )

        # Tab selection
        with solara.Card():
            with solara.Row(style="gap: 10px;"):
                solara.Button(
                    "With Earth Engine",
                    on_click=lambda: selected_tab.set(0),
                    color="primary" if selected_tab.value == 0 else "default",
                )
                solara.Button(
                    "Without Earth Engine",
                    on_click=lambda: selected_tab.set(1),
                    color="primary" if selected_tab.value == 1 else "default",
                )
                solara.Button(
                    "Pattern Comparison",
                    on_click=lambda: selected_tab.set(2),
                    color="primary" if selected_tab.value == 2 else "default",
                )

        # Display selected tab content
        if selected_tab.value == 0:
            AoiWithGEE()
        elif selected_tab.value == 1:
            AoiWithoutGEE()
        else:
            ComparisonExample()
