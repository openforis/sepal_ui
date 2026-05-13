"""Tests for MapAppComponent — the Solara wrapper around MapAppShell."""

import reacton
import solara
from ipywidgets import VBox

from pysepal.sepalwidgets.vue_app import LocaleSelect, ThemeToggle
from pysepal.solara.components.layout import (
    ExternalLink,
    MapAppComponent,
    PanelSection,
    RightPanelConfig,
    StepConfig,
)
from pysepal.solara.components.layout.shell import MapAppShell
from pysepal.solara.theme import ThemeState


def _render(page_fn):
    """Render a Solara component into a kernel and return (box, rc)."""
    return reacton.render(page_fn(), handle_error=False)


def _walk_for(widget, cls):
    """Yield descendants of `widget` that are instances of `cls`."""
    found = []
    stack = [widget]
    while stack:
        w = stack.pop()
        if isinstance(w, cls):
            found.append(w)
        children = getattr(w, "children", ()) or ()
        stack.extend(children)
    return found


def test_map_app_renders_default_shell():
    @solara.component
    def Page():
        MapAppComponent(app_title="Hello", app_icon="mdi-leaf")

    box, _ = _render(Page)
    shells = _walk_for(box, MapAppShell)
    assert len(shells) == 1
    shell = shells[0]
    assert shell.app_title == "Hello"
    assert shell.app_icon == "mdi-leaf"


def test_map_app_passes_sepal_map():
    fake_map = VBox()

    @solara.component
    def Page():
        MapAppComponent(sepal_map=fake_map)

    box, _ = _render(Page)
    shell = _walk_for(box, MapAppShell)[0]
    assert list(shell.main_map) == [fake_map]


def test_theme_state_propagates_to_toggle():
    state = ThemeState(mode="dark")

    @solara.component
    def Page():
        MapAppComponent(theme_state=state)

    box, _ = _render(Page)
    shell = _walk_for(box, MapAppShell)[0]
    assert len(shell.theme_toggle) == 1
    toggle = shell.theme_toggle[0]
    assert isinstance(toggle, ThemeToggle)
    assert toggle.get_theme_state() is state


def test_locale_select_default_present():
    @solara.component
    def Page():
        MapAppComponent()

    box, _ = _render(Page)
    shell = _walk_for(box, MapAppShell)[0]
    assert len(shell.language_selector) == 1
    assert isinstance(shell.language_selector[0], LocaleSelect)


def test_steps_data_serialized():
    @solara.component
    def Step1Body():
        solara.Markdown("step 1")

    @solara.component
    def Page():
        MapAppComponent(
            steps=[
                StepConfig(id=1, name="AOI", icon="mdi-map", display="step", content=Step1Body),
                StepConfig(id=2, name="Process", icon="mdi-cog", display="dialog"),
            ],
            current_step=1,
        )

    box, _ = _render(Page)
    shell = _walk_for(box, MapAppShell)[0]
    assert [s["id"] for s in shell.steps_data] == [1, 2]
    assert [s["display"] for s in shell.steps_data] == ["step", "dialog"]
    assert shell.active_step_content is not None


def test_inactive_step_has_no_content_widget():
    @solara.component
    def Body():
        solara.Markdown("x")

    @solara.component
    def Page():
        MapAppComponent(
            steps=[StepConfig(id=1, name="AOI", content=Body)],
            current_step=None,
        )

    box, _ = _render(Page)
    shell = _walk_for(box, MapAppShell)[0]
    assert shell.active_step_content is None


def test_right_panel_sections_render():
    @solara.component
    def LayersBody():
        solara.Markdown("layers")

    @solara.component
    def LegendBody():
        solara.Markdown("legend")

    @solara.component
    def Page():
        MapAppComponent(
            right_panel_config=RightPanelConfig(title="Tools", width=400),
            right_panel_content=[
                PanelSection(title="Layers", icon="mdi-layers", content=LayersBody),
                PanelSection(
                    title="Legend", icon="mdi-format-list", content=LegendBody, divider=True
                ),
            ],
            right_panel_open=True,
        )

    box, _ = _render(Page)
    shell = _walk_for(box, MapAppShell)[0]
    assert shell.right_panel_open is True
    assert shell.right_panel_config["title"] == "Tools"
    assert shell.right_panel_config["width"] == 400
    assert len(shell.right_panel_sections) == 2
    assert len(shell.right_panel_content_widgets) == 2
    assert shell.right_panel_sections[1]["divider"] is True


def test_external_links_serialized():
    @solara.component
    def Page():
        MapAppComponent(
            external_links=[
                ExternalLink(title="Docs", url="https://docs.example", icon="mdi-book"),
                ExternalLink(title="Repo", url="https://github.com/x/y"),
            ],
        )

    box, _ = _render(Page)
    shell = _walk_for(box, MapAppShell)[0]
    assert len(shell.external_links) == 2
    assert shell.external_links[0]["title"] == "Docs"
    assert shell.external_links[0]["icon"] == "mdi-book"
    assert shell.external_links[1]["icon"] == "mdi-open-in-new"


def test_with_syntax_mounts_children():
    rendered = []

    @solara.component
    def Marker():
        rendered.append("rendered")
        solara.Markdown("inside")

    @solara.component
    def Page():
        with MapAppComponent():
            Marker()

    box, _ = _render(Page)
    shell = _walk_for(box, MapAppShell)[0]
    assert "rendered" in rendered
    assert shell.children_slot is not None


def test_step_change_callback_updates_reactive_state():
    open_step = solara.reactive(None)

    @solara.component
    def Body():
        solara.Markdown("body")

    @solara.component
    def Page():
        MapAppComponent(
            steps=[StepConfig(id=1, name="AOI", content=Body)],
            current_step=open_step,
        )

    box, rc = _render(Page)
    shell = _walk_for(box, MapAppShell)[0]
    # Simulate the Vue → Python event (user clicked a step in the drawer).
    shell.vue_handle_step_activation(1)
    assert open_step.value == 1
    shell.vue_handle_step_deactivation()
    assert open_step.value is None
