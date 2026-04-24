"""Template contract tests for the Vue-backed notification UI."""

import re
from pathlib import Path

_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[3]
    / "pysepal"
    / "solara"
    / "notifications"
    / "NotificationUI.vue"
)


def _rule_body(selector: str) -> str:
    content = _TEMPLATE_PATH.read_text()
    match = re.search(
        rf"{re.escape(selector)}\s*\{{(?P<body>.*?)\n\}}",
        content,
        re.DOTALL,
    )
    assert match, f"Missing CSS rule for {selector}"
    return match.group("body")


def _numeric_property(rule_body: str, name: str) -> int:
    match = re.search(rf"{re.escape(name)}:\s*(\d+);", rule_body)
    assert match, f"Missing numeric property {name}"
    return int(match.group(1))


_DIALOG_Z_INDEX = 202  # Vuetify 2 v-dialog__content default


def test_notification_layers_sit_above_dialogs():
    """Keep pill and toast layers above Vuetify dialog/overlay defaults.

    Notifications are often *about* the dialog (errors, progress) so they must
    remain visible even when a modal is open — otherwise users miss critical
    feedback and assume the app is unresponsive.
    """
    toast_z = _numeric_property(_rule_body(".toast-stack"), "z-index")
    pill_z = _numeric_property(_rule_body(".pill-wrapper"), "z-index")
    assert toast_z > _DIALOG_Z_INDEX, f"toast z-index {toast_z} not above dialog"
    assert pill_z > _DIALOG_Z_INDEX, f"pill z-index {pill_z} not above dialog"


def test_notification_pill_keeps_mapapp_right_offset_hook():
    """Preserve the MapApp-published CSS variable used for right-panel alignment."""
    pill_rule = _rule_body(".pill-wrapper")
    assert "var(--sepal-notification-right-offset, 0px)" in pill_rule
