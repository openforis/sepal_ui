"""Cascading administrative level selector for AOI selection."""

from typing import Callable, Optional, Union

import reacton.ipyvuetify as rv
import solara
from deprecated.sphinx import versionadded

from pysepal.message import ms


@solara.component
@versionadded(version="3.1", reason="Self-contained admin level selector")
def AdminLevelSelector(
    method: str,
    gee: bool = True,
    value: Union[str, solara.Reactive[Optional[str]]] = None,
    on_value: Optional[Callable[[Optional[str]], None]] = None,
    initial: Optional[str] = None,
):
    """Self-contained administrative level selector with cascading dropdowns.

    Manages internal state for cascading admin levels (0, 1, 2) and exposes
    only the final selected admin code. Provides a stable render tree regardless
    of the method (ADMIN0, ADMIN1, ADMIN2).

    Args:
        method: The admin method ("ADMIN0", "ADMIN1", or "ADMIN2")
        gee: Whether to use Earth Engine (GAUL) or FAO WFS (local)
        value: The final selected admin code (output only)
        on_value: Callback when the final admin code changes
        initial: Restore seed — the final admin code of a previously persisted
            selection. Snapshotted at mount; the full cascade (parent levels
            included) is seeded from it exactly once. Remount the component to
            restore a different selection.

    Returns:
        None. The final admin code is passed through value/on_value.

    Example:
        ```python
        @solara.component
        def MyApp():
            admin_code = solara.use_reactive(None)

            AdminLevelSelector(
                method="ADMIN1",
                gee=False,
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

    items_0 = solara.use_reactive([])
    items_1 = solara.use_reactive([])
    items_2 = solara.use_reactive([])

    loading_0 = solara.use_reactive(False)
    loading_1 = solara.use_reactive(False)
    loading_2 = solara.use_reactive(False)

    target_level = {"ADMIN0": 0, "ADMIN1": 1, "ADMIN2": 2}.get(method, 0)

    # Snapshot the restore seed at first mount. Callers (AoiView) may bind
    # `initial` live to the same reactive this component drives via `value`, and
    # update_output resets that reactive to None on mount before the async
    # cascade seeds — so reading `initial` live would wipe the restore chain to
    # {} and leave the dropdowns empty. Freezing it (deps=[]) keeps the chain
    # stable; a genuine re-restore remounts the component.
    initial_seed = solara.use_memo(lambda: initial, [])

    def _compute_chain():
        # Local import breaks the cycle: aoi/__init__ -> aoi_view -> this module.
        from pysepal.solara.components.aoi.admin import admin_parent_chain

        return admin_parent_chain(method, initial_seed)

    _chain = solara.use_memo(_compute_chain, [method, initial_seed])
    # Levels auto-seeded from the restore chain. A per-level one-shot guard (not a
    # shared flag) so the async loaders can seed in any order, exactly once each,
    # and a later genuine user change of a parent still resets its children.
    _seeded = solara.use_ref(set())

    # The (parent, target_level) each child loader last processed. Under reacton's
    # double effect-run the loaders fire twice per dependency change; the second,
    # redundant run for an UNCHANGED parent would otherwise take the else-branch
    # and wipe the value the first run just restored from the chain (leaving the
    # dropdowns empty on restore). Short-circuiting on an unchanged parent keeps
    # the seed and skips a duplicate fetch; a genuine parent change still flows
    # through to reseed or clear stale children.
    _UNSET = solara.use_memo(lambda: object(), [])
    _level1_parent = solara.use_ref(_UNSET)
    _level2_parent = solara.use_ref(_UNSET)

    async def _load_level_0():
        # Local import breaks the cycle: aoi/__init__ -> aoi_view -> this module.
        from pysepal.solara.components.aoi.admin import fetch_admin_items

        loading_0.set(True)
        try:
            items = fetch_admin_items(level=0, parent_code="")
            items_0.set(items)
            if _chain.get(0) and 0 not in _seeded.current:
                _seeded.current = _seeded.current | {0}
                level_0.set(_chain[0])
        finally:
            loading_0.set(False)

    solara.lab.use_task(_load_level_0, dependencies=[], raise_error=False)

    async def _load_level_1():
        from pysepal.solara.components.aoi.admin import fetch_admin_items

        key = (level_0.value, target_level)
        if _level1_parent.current == key:
            return
        _level1_parent.current = key

        if level_0.value and target_level >= 1:
            loading_1.set(True)
            try:
                items = fetch_admin_items(level=1, parent_code=level_0.value)
                items_1.set(items)
                if _chain.get(1) and 1 not in _seeded.current:
                    _seeded.current = _seeded.current | {1}
                    level_1.set(_chain[1])
                else:
                    level_1.set(None)
            finally:
                loading_1.set(False)
        else:
            items_1.set([])
            level_1.set(None)
        level_2.set(None)
        items_2.set([])

    solara.lab.use_task(
        _load_level_1,
        dependencies=[level_0.value, target_level],
        raise_error=False,
    )

    async def _load_level_2():
        from pysepal.solara.components.aoi.admin import fetch_admin_items

        key = (level_1.value, target_level)
        if _level2_parent.current == key:
            return
        _level2_parent.current = key

        if level_1.value and target_level >= 2:
            loading_2.set(True)
            try:
                items = fetch_admin_items(level=2, parent_code=level_1.value)
                items_2.set(items)
                if _chain.get(2) and 2 not in _seeded.current:
                    _seeded.current = _seeded.current | {2}
                    level_2.set(_chain[2])
                else:
                    level_2.set(None)
            finally:
                loading_2.set(False)
        else:
            items_2.set([])
            level_2.set(None)

    solara.lab.use_task(
        _load_level_2,
        dependencies=[level_1.value, target_level],
        raise_error=False,
    )

    def update_output():
        if target_level == 0:
            reactive_value.set(level_0.value)
        elif target_level == 1:
            reactive_value.set(level_1.value)
        elif target_level == 2:
            reactive_value.set(level_2.value)

    solara.use_effect(update_output, [level_0.value, level_1.value, level_2.value, target_level])

    with solara.Column(classes="pa-0 ma-0", style="gap: 8px;"):
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
