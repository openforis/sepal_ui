"""Unit tests for tests._janitor."""

from __future__ import annotations

import argparse
import datetime as dt
from unittest.mock import MagicMock

import ee
import pytest

from tests import _janitor


def _rfc3339(moment: dt.datetime) -> str:
    """Render a datetime in the format GEE returns in updateTime."""
    return moment.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def test_parse_max_age_hours():
    assert _janitor._parse_max_age("24h") == dt.timedelta(hours=24)


def test_parse_max_age_days():
    assert _janitor._parse_max_age("7d") == dt.timedelta(days=7)


def test_parse_max_age_zero():
    assert _janitor._parse_max_age("0") == dt.timedelta(0)


def test_parse_max_age_invalid():
    with pytest.raises(argparse.ArgumentTypeError):
        _janitor._parse_max_age("7x")


def test_parse_max_age_negative_rejected():
    with pytest.raises(argparse.ArgumentTypeError):
        _janitor._parse_max_age("-1h")


def test_list_stale_filters_by_age():
    now = dt.datetime(2026, 4, 20, 12, 0, tzinfo=dt.timezone.utc)
    list_fn = MagicMock(
        return_value={
            "assets": [
                {
                    "name": "projects/x/assets/pysepal-tests/sepal-ui-aaa",
                    "updateTime": _rfc3339(now - dt.timedelta(hours=48)),
                },
                {
                    "name": "projects/x/assets/pysepal-tests/sepal-ui-bbb",
                    "updateTime": _rfc3339(now - dt.timedelta(hours=1)),
                },
            ]
        }
    )
    stale = _janitor._list_stale(
        "projects/x/assets/pysepal-tests",
        dt.timedelta(hours=24),
        now=now,
        list_fn=list_fn,
    )
    assert len(stale) == 1
    assert stale[0]["id"].endswith("sepal-ui-aaa")


def test_list_stale_max_age_zero_returns_all():
    now = dt.datetime(2026, 4, 20, 12, 0, tzinfo=dt.timezone.utc)
    list_fn = MagicMock(
        return_value={
            "assets": [
                {
                    "name": "projects/x/assets/pysepal-tests/sepal-ui-aaa",
                    "updateTime": _rfc3339(now - dt.timedelta(minutes=1)),
                },
            ]
        }
    )
    stale = _janitor._list_stale(
        "projects/x/assets/pysepal-tests",
        dt.timedelta(0),
        now=now,
        list_fn=list_fn,
    )
    assert len(stale) == 1


def test_list_stale_container_missing_returns_empty():
    list_fn = MagicMock(
        side_effect=ee.EEException("Asset 'projects/x/assets/pysepal-tests' not found")
    )
    stale = _janitor._list_stale(
        "projects/x/assets/pysepal-tests",
        dt.timedelta(0),
        list_fn=list_fn,
    )
    assert stale == []


def test_list_stale_permission_error_is_reraised():
    list_fn = MagicMock(side_effect=ee.EEException("Permission denied for user"))
    with pytest.raises(ee.EEException):
        _janitor._list_stale(
            "projects/x/assets/pysepal-tests",
            dt.timedelta(0),
            list_fn=list_fn,
        )
