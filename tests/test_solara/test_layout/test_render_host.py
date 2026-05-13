"""Tests for SolaraRenderHost."""

import solara
from ipywidgets import VBox

from pysepal.solara.components.layout.render_host import SolaraRenderHost


def test_host_starts_empty():
    host = SolaraRenderHost()
    assert isinstance(host, VBox)
    assert host.children == ()


def test_host_renders_solara_component():
    @solara.component
    def Hello():
        solara.Markdown("hi")

    host = SolaraRenderHost()
    host.set_render(Hello)
    assert len(host.children) >= 1


def test_host_clears_when_render_is_none():
    @solara.component
    def Hello():
        solara.Markdown("hi")

    host = SolaraRenderHost()
    host.set_render(Hello)
    assert len(host.children) >= 1

    host.set_render(None)
    assert host.children == ()


def test_host_replaces_previous_render():
    @solara.component
    def A():
        solara.Markdown("a")

    @solara.component
    def B():
        solara.Markdown("b")

    host = SolaraRenderHost()
    host.set_render(A)
    assert len(host.children) >= 1

    host.set_render(B)
    assert len(host.children) >= 1
