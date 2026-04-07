"""AOI All Methods Test Page.

Test page for verifying all AOI selection methods including the newly added
SHAPE, POINTS, and ASSET methods.

To run:

```bash
pysepal$ SOLARA_TEST=true ./run_solara.sh pysepal/templates/solara/solara_map_app/aoi_all_methods.py --port 8901
```
"""

from pathlib import Path

import solara

from pysepal import mapping as sm
from pysepal.sepalwidgets.vue_app import ThemeToggle
from pysepal.solara import (
    get_current_gee_interface,
    setup_sessions,
    setup_solara_server,
    setup_theme_colors,
    with_sepal_sessions,
)
from pysepal.solara.components.aoi import AoiView

DUMMY_DATA_DIR = Path(__file__).resolve().parents[4] / "tests" / "data" / "aoi_manual"

# 1. Server setup (module level)
setup_solara_server(extra_asset_locations=[])


# 2. Session setup (per kernel)
@solara.lab.on_kernel_start
def on_kernel_start():
    """Set up sessions management."""
    return setup_sessions()


@solara.component
def AoiTestAllMethods(gee: bool = True, gee_interface=None):
    """Test all AOI methods with a map.

    Args:
        gee: Whether to enable GEE.
        gee_interface: Session-backed GEEInterface from the current Solara session.
    """
    aoi_data = solara.use_reactive(None)
    aoi_loading = solara.use_reactive(False)
    clear_aoi_ref = solara.use_ref(None)

    theme_toggle = ThemeToggle()

    def build_map():
        map_ = sm.SepalMap(
            zoom=2,
            center=[0, 0],
            gee=gee,
            gee_interface=gee_interface if gee else None,
            theme_toggle=theme_toggle,
        )
        return map_

    sepal_map = solara.use_memo(build_map, [gee, id(gee_interface)])

    with solara.Column(style="padding: 20px; gap: 20px;"):
        solara.Markdown(f"## All Methods (GEE={'enabled' if gee else 'disabled'})")

        with solara.Columns([1, 1], style="gap: 20px;"):
            with solara.Column():
                AoiView(
                    value=aoi_data,
                    loading=aoi_loading,
                    methods="ALL",
                    map_=sepal_map,
                    gee=gee,
                    file_initial_folder=str(DUMMY_DATA_DIR),
                    clear_ref=clear_aoi_ref,
                )

            with solara.Card("Map", style="height: 500px;"):
                solara.display(sepal_map)

        # Result display
        with solara.Card("Result"):
            if aoi_loading.value:
                solara.ProgressLinear(True)
                solara.Info("Processing...")

            if aoi_data.value:
                solara.Success(f"AOI selected: {aoi_data.value.name}")
                with solara.Column(style="gap: 4px;"):
                    solara.Text(f"Method: {aoi_data.value.method}")
                    solara.Text(f"Name: {aoi_data.value.name}")
                    solara.Text(f"GEE: {aoi_data.value.gee}")
                    solara.Text(f"Has GDF: {aoi_data.value.gdf is not None}")
                    solara.Text(
                        f"Has EE object: " f"{aoi_data.value.feature_collection is not None}"
                    )
                    if aoi_data.value.gdf is not None:
                        solara.Text(f"Features: {len(aoi_data.value.gdf)}")
                        solara.Text(
                            f"Columns: {', '.join(c for c in aoi_data.value.gdf.columns if c != 'geometry')}"
                        )

                solara.Button(
                    "Clear",
                    on_click=lambda: clear_aoi_ref.current() if clear_aoi_ref.current else None,
                    color="error",
                    outlined=True,
                    small=True,
                )
            else:
                solara.Info("No AOI selected yet")


@solara.component
def AoiTestCustomMethods():
    """Test only custom methods (SHAPE, DRAW, POINTS)."""
    aoi_data = solara.use_reactive(None)
    aoi_loading = solara.use_reactive(False)

    theme_toggle = ThemeToggle()

    sepal_map = solara.use_memo(
        lambda: sm.SepalMap(
            zoom=2,
            center=[0, 0],
            gee=False,
            theme_toggle=theme_toggle,
        ),
        [],
    )

    with solara.Column(style="padding: 20px; gap: 20px;"):
        solara.Markdown("## Custom Methods Only")
        solara.Markdown("Tests: SHAPE, DRAW, POINTS (no admin boundaries)")

        with solara.Columns([1, 1], style="gap: 20px;"):
            with solara.Column():
                AoiView(
                    value=aoi_data,
                    loading=aoi_loading,
                    methods="CUSTOM",
                    map_=sepal_map,
                    gee=False,
                    file_initial_folder=str(DUMMY_DATA_DIR),
                )

            with solara.Card("Map", style="height: 500px;"):
                solara.display(sepal_map)

        if aoi_data.value:
            with solara.Card("Result"):
                solara.Success(f"{aoi_data.value.method}: {aoi_data.value.name}")
                if aoi_data.value.gdf is not None:
                    solara.Text(f"Features: {len(aoi_data.value.gdf)}")


@solara.component
@with_sepal_sessions(module_name="aoi_test")
def Page():
    """Main test page with tabs for different AOI configurations."""
    setup_theme_colors()

    gee_interface = get_current_gee_interface()

    selected_tab = solara.use_reactive(0)

    with solara.Column(style="padding: 20px; gap: 20px;"):
        solara.Markdown("# AOI Methods Test Page")
        solara.Markdown("Verify all AOI selection methods work correctly.")
        solara.Info(f"Local SHAPE and POINTS pickers start in: {DUMMY_DATA_DIR}")

        with solara.Card():
            # Keep all tab panels mounted so state survives tab switches.
            with solara.Column(style="gap: 0;"):
                with solara.Column(
                    style=("display: block;" if selected_tab.value == 0 else "display: none;")
                ):
                    AoiTestAllMethods(
                        gee=True,
                        gee_interface=gee_interface,
                    )
