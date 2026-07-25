"""Regression tests for restoring a multi-level admin AOI cascade.

Reproduces the bug where restoring a saved ADMIN1 selection (e.g.
Paraguay > Amambay) left both cascade dropdowns empty: ``AoiView`` binds the
selector's restore seed ``initial`` to the live ``admin_code`` reactive, which
the selector itself resets to ``None`` (via ``update_output``) on mount before
the async cascade seeds — wiping the restore chain.
"""

import time

import solara

import pysepal.solara.components.aoi.admin as admin_mod
from pysepal.solara.components.inputs.admin_selector import AdminLevelSelector

# Paraguay (206) > Amambay (2184); Algeria (101) > Adrar (1001) > Adrar (100001).
_CHAINS = {
    "2184": {0: "206", 1: "2184"},
    "100001": {0: "101", 1: "1001", 2: "100001"},
}


def _fake_chain(method, code):
    return dict(_CHAINS.get(str(code), {}))


def _fake_fetch(level, parent_code):
    # Mirrors fetch_admin_items' item shape.
    mapping = {
        (0, ""): [
            {"text": "Paraguay", "value": "206"},
            {"text": "Algeria", "value": "101"},
        ],
        (1, "206"): [{"text": "Amambay", "value": "2184"}],
        (1, "101"): [{"text": "Adrar", "value": "1001"}],
        (2, "1001"): [{"text": "Adrar", "value": "100001"}],
    }
    return mapping.get((level, str(parent_code)), [])


@solara.component
def _RestoreHarness(method, admin_code):
    # Mirrors AoiView: the restore seed `initial` is bound live to the same
    # reactive the selector drives.
    AdminLevelSelector(
        method=method,
        gee=True,
        value=admin_code,
        initial=admin_code.value,
    )


def _settle(admin_code, expected, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline and admin_code.value != expected:
        time.sleep(0.05)
    # Give a redundant double-run a chance to wrongly wipe the value before asserting.
    time.sleep(0.5)


def test_admin1_cascade_restores_seeded_value(monkeypatch):
    monkeypatch.setattr(admin_mod, "fetch_admin_items", _fake_fetch)
    monkeypatch.setattr(admin_mod, "admin_parent_chain", _fake_chain, raising=False)

    # The restored final code is present at mount (the app set it before mount).
    admin_code = solara.reactive("2184")
    box, rc = solara.render(_RestoreHarness("ADMIN1", admin_code), handle_error=False)
    try:
        _settle(admin_code, "2184")
        assert admin_code.value == "2184", (
            f"cascade failed to restore admin code; admin_code={admin_code.value!r}"
        )
    finally:
        rc.close()


def test_admin2_cascade_restores_full_chain(monkeypatch):
    monkeypatch.setattr(admin_mod, "fetch_admin_items", _fake_fetch)
    monkeypatch.setattr(admin_mod, "admin_parent_chain", _fake_chain, raising=False)

    admin_code = solara.reactive("100001")
    box, rc = solara.render(_RestoreHarness("ADMIN2", admin_code), handle_error=False)
    try:
        _settle(admin_code, "100001")
        assert admin_code.value == "100001", (
            f"ADMIN2 cascade failed to restore; admin_code={admin_code.value!r}"
        )
    finally:
        rc.close()
