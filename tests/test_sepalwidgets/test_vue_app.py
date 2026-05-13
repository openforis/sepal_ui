"""Tests for the legacy MapApp compatibility shim."""

import warnings


def test_legacy_mapapp_emits_deprecation_warning():
    from pysepal.sepalwidgets.vue_app import MapApp

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        MapApp()
    deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert deprecations, "Expected a DeprecationWarning from legacy MapApp()"
    assert "MapAppComponent" in str(deprecations[0].message)


def test_mapapp_component_re_exported_from_solara():
    from pysepal.solara import MapAppComponent
    from pysepal.solara.components.layout import MapAppComponent as Canonical

    assert MapAppComponent is Canonical
