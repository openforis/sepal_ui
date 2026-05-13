"""MapAppComponent — Solara-native MapApp layout.

A first-class Solara component that wraps :class:`MapAppShell` with
typed dataclass props, reactive state, and `with MapAppComponent(...): ...`
context-manager support. The shell, theme toggle, locale selector, and
content hosts are memoized so widget identity is stable across renders.
"""

from __future__ import annotations

from typing import Callable, Optional, Sequence, Union
from typing import List as TList

import solara
from ipywidgets import DOMWidget

from pysepal.solara.theme import ThemeState, get_current_theme_state

from .models import (
    ExternalLink,
    PanelSection,
    RightPanelConfig,
    StepConfig,
)
from .render_host import SolaraRenderHost
from .shell import MapAppShell

try:
    # Optional import — translator is only required when callers want
    # to drive the locale selector.
    from pysepal.translator import Translator
except Exception:  # pragma: no cover - translator is part of pysepal
    Translator = None  # type: ignore[assignment,misc]


def _steps_to_json(steps: Sequence[StepConfig]) -> list:
    """Serialize StepConfig dataclasses to Vue-friendly JSON.

    The Solara-side render callable (`step.content`) is intentionally
    omitted — the active step's widget is exposed through the
    `active_step_content` trait instead.
    """
    out = []
    for step in steps:
        out.append(
            {
                "id": step.id,
                "name": step.name,
                "icon": step.icon,
                "display": step.display,
                "right_panel_action": step.right_panel_action or "",
                "content_enabled": step.content_enabled,
                "actions": [
                    {"label": a.label, "event": a.event, "cancel": a.cancel} for a in step.actions
                ],
                "width": step.width or 0,
                "height": step.height or 0,
            }
        )
    return out


def _panel_sections_to_json(sections: Sequence[PanelSection]) -> list:
    """Serialize PanelSection dataclasses (without their content)."""
    return [
        {
            "title": s.title,
            "icon": s.icon,
            "divider": s.divider,
            "description": s.description,
        }
        for s in sections
    ]


def _build_theme_toggle(theme_state: ThemeState):
    """Construct a session-bound `ThemeToggle` widget (lazy import)."""
    from pysepal.sepalwidgets.vue_app import ThemeToggle

    return ThemeToggle(theme_state=theme_state)


def _build_locale_select(translator):
    """Construct a `LocaleSelect` widget bound to the given translator."""
    from pysepal.sepalwidgets.vue_app import LocaleSelect

    return LocaleSelect(translator=translator)


@solara.component
def MapAppComponent(
    app_title: str = "Map Application",
    app_icon: str = "mdi-earth",
    sepal_map: Optional[DOMWidget] = None,
    steps: Sequence[StepConfig] = (),
    right_panel_config: Optional[RightPanelConfig] = None,
    right_panel_content: Sequence[PanelSection] = (),
    right_panel_open: Union[bool, solara.Reactive[bool]] = False,
    current_step: Union[Optional[int], solara.Reactive[Optional[int]]] = None,
    initial_step: Optional[int] = None,
    theme_state: Optional[ThemeState] = None,
    translator=None,
    external_links: Sequence[ExternalLink] = (),
    repo_url: str = "",
    docs_url: str = "",
    dialog_width: int = 800,
    dialog_fullscreen: bool = False,
    on_step_action: Optional[Callable[[int, str], None]] = None,
    on_right_panel_toggle: Optional[Callable[[bool], None]] = None,
    children: list = [],
) -> None:
    """Render the MapApp layout as a Solara component.

    See `docs/guides/solara-mapapp-component.md` for usage and migration
    guidance.

    Args:
        app_title: Drawer header title.
        app_icon: Drawer header icon name.
        sepal_map: Map widget rendered in the main area.
        steps: Typed list of `StepConfig` entries.
        right_panel_config: Display configuration for the right panel.
            Required when `right_panel_content` is non-empty.
        right_panel_content: Typed list of `PanelSection` entries.
        right_panel_open: Reactive boolean controlling panel visibility.
        current_step: Reactive currently-active step id.
        initial_step: Step id auto-activated on first render.
        theme_state: Session-scoped theme state; falls back to
            `get_current_theme_state()`.
        translator: Optional pysepal `Translator` driving the locale
            selector. Locale changes update the translator and
            persist via `pysepal.scripts.utils.set_config`.
        external_links: Typed list of `ExternalLink` tiles for the
            drawer footer.
        repo_url: Repository URL (also surfaces auto-derived Source /
            Docs / Bug links).
        docs_url: Documentation URL (used only when `repo_url` is set).
        dialog_width: Default width for `display="dialog"` steps.
        dialog_fullscreen: Whether dialog steps render full-screen.
        on_step_action: Optional callback for footer action buttons —
            invoked as `on_step_action(step_id, event)`.
        on_right_panel_toggle: Optional callback for right-panel
            open/close — invoked as `on_right_panel_toggle(open)`.
        children: Captured automatically when the component is used as
            `with MapAppComponent(...): ...` — rendered in a slot in the
            main area.
    """
    resolved_theme = theme_state or get_current_theme_state()
    current_step_reactive = solara.use_reactive(current_step)
    right_panel_open_reactive = solara.use_reactive(right_panel_open)

    # Persistent widgets — created once per component instance.
    theme_toggle_widget = solara.use_memo(
        lambda: _build_theme_toggle(resolved_theme), dependencies=[]
    )
    if theme_toggle_widget.get_theme_state() is not resolved_theme:
        theme_toggle_widget.bind_theme_state(resolved_theme)

    locale_select_widget = solara.use_memo(
        lambda: _build_locale_select(translator), dependencies=[]
    )

    step_host: SolaraRenderHost = solara.use_memo(lambda: SolaraRenderHost(), dependencies=[])
    children_host: SolaraRenderHost = solara.use_memo(lambda: SolaraRenderHost(), dependencies=[])

    # Right-panel section hosts — recreated when the number of sections
    # changes (cheap; widgets are released by Reacton's reconciler).
    panel_hosts: TList[SolaraRenderHost] = solara.use_memo(
        lambda: [SolaraRenderHost() for _ in right_panel_content],
        dependencies=[len(right_panel_content)],
    )
    for host, section in zip(panel_hosts, right_panel_content):
        host.set_render(section.content)

    # Resolve the active step's content factory.
    active_id = current_step_reactive.value
    active_step: Optional[StepConfig] = next((s for s in steps if s.id == active_id), None)
    if active_step is not None and active_step.content is not None:
        step_host.set_render(active_step.content)
        active_step_content = step_host
    else:
        step_host.set_render(None)
        active_step_content = None

    # Children slot — only mount the host when there are children.
    if children:
        children_host.set_elements(children)
        children_widget: Optional[DOMWidget] = children_host
    else:
        children_host.set_render(None)
        children_widget = None

    # Bind the embedded map to the resolved theme state.
    if sepal_map is not None and hasattr(sepal_map, "bind_theme_state"):
        sepal_map.bind_theme_state(resolved_theme)

    # Internal callbacks that bridge shell events → Solara reactives.
    def _on_step_change(step_id, is_open):
        current_step_reactive.set(step_id if is_open else None)

    def _on_right_panel_toggle(value: bool) -> None:
        right_panel_open_reactive.set(bool(value))
        if on_right_panel_toggle is not None:
            on_right_panel_toggle(bool(value))

    def _on_step_action(step_id: int, event: str) -> None:
        if on_step_action is not None:
            on_step_action(int(step_id), str(event))

    # Serialize the shell's reactive props.
    config_dict = (
        {
            "title": right_panel_config.title,
            "icon": right_panel_config.icon,
            "width": right_panel_config.width,
            "description": right_panel_config.description,
            "toggle_icon": right_panel_config.toggle_icon,
        }
        if right_panel_config is not None
        else {}
    )

    return MapAppShell.element(
        app_title=app_title,
        app_icon=app_icon,
        repo_url=repo_url,
        docs_url=docs_url,
        dialog_width=dialog_width,
        dialog_fullscreen=dialog_fullscreen,
        main_map=[sepal_map] if sepal_map is not None else [],
        theme_toggle=[theme_toggle_widget],
        language_selector=[locale_select_widget],
        steps_data=_steps_to_json(steps),
        active_step_content=active_step_content,
        children_slot=children_widget,
        right_panel_config=config_dict,
        right_panel_sections=_panel_sections_to_json(right_panel_content),
        right_panel_content_widgets=list(panel_hosts),
        right_panel_open=bool(right_panel_open_reactive.value),
        right_panel_width=(right_panel_config.width if right_panel_config is not None else 300),
        external_links=[
            {"title": link.title, "url": link.url, "icon": link.icon} for link in external_links
        ],
        initial_step=initial_step,
        current_step=current_step_reactive.value,
        on_step_change=_on_step_change,
        on_right_panel_toggle=_on_right_panel_toggle,
        on_step_action=_on_step_action,
    )
