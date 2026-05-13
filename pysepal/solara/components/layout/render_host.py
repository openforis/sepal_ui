"""Bridge a Solara/Reacton render function into an ipywidget container.

`SolaraRenderHost` is a `VBox` whose children are managed by a Reacton
render context. Use it to embed Solara content inside a
`VuetifyTemplate` trait (where only ipywidget instances are allowed).
"""

from __future__ import annotations

from typing import Callable, Optional

import reacton
from ipywidgets import VBox

RenderFactory = Callable[[], None]


class SolaraRenderHost(VBox):
    """A VBox whose contents are rendered by a Solara/Reacton component."""

    def __init__(self) -> None:
        """Create an empty host with no active render context."""
        super().__init__(children=())
        self._render_context = None
        self._current_factory: Optional[RenderFactory] = None

    def set_render(self, factory: Optional[RenderFactory]) -> None:
        """Mount the given Solara component or clear the host.

        Calling with the same factory is a no-op (idempotent). Passing
        None tears down the active render and empties the host.
        """
        if factory is self._current_factory:
            return

        self._dispose_render()
        self._current_factory = factory

        if factory is None:
            self.children = ()
            return

        element = factory()
        if element is None:
            # The factory rendered via side-effects (e.g. solara.Markdown
            # inside its body) — wrap it as a Reacton Element.
            try:
                element = reacton.core.Element(factory)  # type: ignore[attr-defined]
            except Exception:  # pragma: no cover - defensive
                self.children = ()
                return

        _, self._render_context = reacton.render(element, container=self, handle_error=False)

    def set_elements(self, elements) -> None:
        """Render a pre-constructed list of Reacton elements.

        Use this when children come from a `with MapAppComponent(): ...`
        block — the elements already exist and must not be re-evaluated.
        """
        from ipywidgets import VBox as _VBox

        self._dispose_render()
        self._current_factory = None
        if not elements:
            self.children = ()
            return
        wrapper = _VBox.element(children=list(elements))
        _, self._render_context = reacton.render(wrapper, container=self, handle_error=False)

    def _dispose_render(self) -> None:
        """Close any active render context and detach its children."""
        if self._render_context is not None:
            try:
                self._render_context.close()
            except Exception:
                pass
            self._render_context = None
        self.children = ()

    def close(self) -> None:
        """Release the render context before the widget is collected."""
        self._dispose_render()
        super().close()
