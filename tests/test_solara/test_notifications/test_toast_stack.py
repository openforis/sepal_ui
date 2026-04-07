"""Tests for ToastStack helper logic (non-component, pure Python)."""

import time

from pysepal.solara.notifications.state import Toast, ToastType
from pysepal.solara.notifications.toast_stack import (
    ERROR_ROTATION_SECONDS,
    visible_toasts,
)


class TestVisibleToasts:
    def test_max_three_visible(self):
        toasts = [Toast(message=f"msg-{i}") for i in range(5)]
        visible = visible_toasts(toasts)
        assert len(visible) == 3

    def test_newest_first(self):
        now = time.time()
        toasts = [
            Toast(message="old", created_at=now - 10),
            Toast(message="mid", created_at=now - 5),
            Toast(message="new", created_at=now),
        ]
        visible = visible_toasts(toasts)
        assert visible[0].message == "new"
        assert visible[2].message == "old"

    def test_errors_rotate_after_timeout(self):
        now = time.time()
        old_errors = [
            Toast(
                message=f"err-{i}",
                type=ToastType.ERROR,
                created_at=now - ERROR_ROTATION_SECONDS - 10,
            )
            for i in range(3)
        ]
        new_info = Toast(message="info", type=ToastType.INFO, created_at=now)
        toasts = old_errors + [new_info]
        visible = visible_toasts(toasts, now=now)
        # Old errors should be rotated out, new info should be visible
        info_visible = [t for t in visible if t.type == ToastType.INFO]
        assert len(info_visible) == 1

    def test_fresh_errors_are_not_rotated(self):
        now = time.time()
        fresh_error = Toast(message="err", type=ToastType.ERROR, created_at=now - 5)
        toasts = [fresh_error]
        visible = visible_toasts(toasts, now=now)
        assert len(visible) == 1
        assert visible[0].type == ToastType.ERROR
