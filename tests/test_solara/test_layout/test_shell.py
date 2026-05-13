"""Tests for the MapAppShell VuetifyTemplate."""

from ipywidgets import VBox

from pysepal.solara.components.layout.shell import MapAppShell


def test_shell_defaults():
    shell = MapAppShell()
    assert shell.app_title == "Map Application"
    assert shell.app_icon == "mdi-earth"
    assert shell.steps_data == []
    assert shell.right_panel_config == {}
    assert shell.right_panel_sections == []
    assert list(shell.right_panel_content_widgets) == []
    assert shell.active_step_content is None
    assert shell.children_slot is None
    assert shell.right_panel_open is False
    assert shell.current_step is None


def test_shell_accepts_main_map_widget():
    box = VBox()
    shell = MapAppShell(main_map=[box])
    assert list(shell.main_map) == [box]


def test_shell_active_step_content_assignment():
    host = VBox()
    shell = MapAppShell()
    shell.active_step_content = host
    assert shell.active_step_content is host


def test_shell_vue_handlers_update_traits():
    shell = MapAppShell()
    shell.vue_handle_step_change(2, True)
    assert shell.current_step == 2
    assert shell.step_open is True

    shell.vue_handle_step_change(2, False)
    assert shell.current_step is None
    assert shell.step_open is False

    shell.vue_set_drawer_width(220)
    assert shell.drawer_width == 220

    shell.vue_set_window_size({"w": 1024, "h": 768})
    assert shell.window_width == 1024
    assert shell.window_height == 768

    shell.vue_set_right_panel_open(True)
    assert shell.right_panel_open is True


def test_shell_step_action_callback():
    captured = []

    def on_action(step_id: int, event: str) -> None:
        captured.append((step_id, event))

    shell = MapAppShell()
    shell.on_step_action = on_action
    shell.vue_handle_step_action(7, "confirm")
    assert captured == [(7, "confirm")]


def test_shell_step_change_callback():
    captured = []

    def on_change(step_id, is_open):
        captured.append((step_id, is_open))

    shell = MapAppShell()
    shell.on_step_change = on_change
    shell.vue_handle_step_activation(3)
    shell.vue_handle_step_deactivation()
    assert captured == [(3, True), (None, False)]


def test_shell_right_panel_action_callback():
    captured = []

    def on_toggle(value):
        captured.append(value)

    shell = MapAppShell()
    shell.on_right_panel_toggle = on_toggle
    shell.vue_handle_right_panel_action("open")
    shell.vue_handle_right_panel_action("close")
    shell.vue_handle_right_panel_action("toggle")
    assert captured == [True, False, True]
