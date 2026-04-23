"""Tests for notification state model."""

from pysepal.solara.notifications.state import Toast, ToastType


def test_toast_effective_timeout_uses_default():
    assert Toast(message="ok", type=ToastType.SUCCESS).effective_timeout() == 3.0


def test_toast_effective_timeout_explicit_overrides():
    assert Toast(message="ok", type=ToastType.SUCCESS, timeout=20.0).effective_timeout() == 20.0
