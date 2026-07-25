"""Tests for admin_parent_chain (GAUL parent-chain lookup for cascade restore)."""

import pandas as pd
import pygaul
import pytest

from pysepal.solara.components.aoi import admin as admin_mod


@pytest.fixture
def fake_gaul(monkeypatch):
    df = pd.DataFrame(
        {
            "gaul0_code": [197, 206, 101],
            "gaul1_code": [pd.NA, 2184, 1001],
            "gaul2_code": [pd.NA, pd.NA, 100001],
        }
    )
    monkeypatch.setattr(pygaul, "_df", lambda: df)
    return df


def test_admin0_returns_single_level(fake_gaul):
    assert admin_mod.admin_parent_chain("ADMIN0", "197") == {0: "197"}


def test_admin1_includes_parent_level0(fake_gaul):
    assert admin_mod.admin_parent_chain("ADMIN1", "2184") == {0: "206", 1: "2184"}


def test_admin2_includes_full_parent_chain(fake_gaul):
    assert admin_mod.admin_parent_chain("ADMIN2", "100001") == {
        0: "101",
        1: "1001",
        2: "100001",
    }


def test_unknown_code_returns_empty(fake_gaul):
    assert admin_mod.admin_parent_chain("ADMIN0", "99999999") == {}


def test_falsy_code_returns_empty(fake_gaul):
    assert admin_mod.admin_parent_chain("ADMIN1", None) == {}
    assert admin_mod.admin_parent_chain("ADMIN2", "") == {}


def test_lookup_failure_returns_empty(monkeypatch):
    def _boom():
        raise RuntimeError("parquet unavailable")

    monkeypatch.setattr(pygaul, "_df", _boom)
    assert admin_mod.admin_parent_chain("ADMIN1", "2184") == {}
