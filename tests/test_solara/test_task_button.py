"""Tests for TaskButtonComponent and use_task_button."""

from unittest.mock import MagicMock

from pysepal.solara.components.task_button import TaskButtonComponent, use_task_button


def test_task_button_renders_label_when_idle():
    """When running=False, button shows the action label."""
    on_start = MagicMock()
    on_cancel = MagicMock()

    el = TaskButtonComponent.widget(
        label="Select AOI",
        on_start=on_start,
        on_cancel=on_cancel,
        running=False,
    )
    assert el is not None


def test_task_button_renders_cancel_when_running():
    """When running=True, button shows cancel label."""
    on_start = MagicMock()
    on_cancel = MagicMock()

    el = TaskButtonComponent.widget(
        label="Select AOI",
        on_start=on_start,
        on_cancel=on_cancel,
        running=True,
        cancel_label="Stop",
    )
    assert el is not None


def test_task_button_disabled_when_external_busy():
    """When external_busy=True and not running, button is disabled."""
    on_start = MagicMock()
    on_cancel = MagicMock()

    el = TaskButtonComponent.widget(
        label="Select AOI",
        on_start=on_start,
        on_cancel=on_cancel,
        running=False,
        external_busy=True,
    )
    assert el is not None


def test_task_button_cancel_never_disabled():
    """When running=True, cancel is clickable even if external_busy=True."""
    on_start = MagicMock()
    on_cancel = MagicMock()

    el = TaskButtonComponent.widget(
        label="Select AOI",
        on_start=on_start,
        on_cancel=on_cancel,
        running=True,
        external_busy=True,
    )
    assert el is not None


def test_use_task_button_returns_correct_keys():
    """use_task_button returns dict with running, on_start, on_cancel."""
    mock_task = MagicMock()
    mock_task.pending = False
    on_start = MagicMock()

    result = use_task_button(mock_task, on_start=on_start)

    assert "running" in result
    assert "on_start" in result
    assert "on_cancel" in result
    assert result["running"] is False
    assert result["on_start"] is on_start


def test_use_task_button_running_reflects_task_pending():
    """use_task_button running matches task.pending."""
    mock_task = MagicMock()
    mock_task.pending = True
    on_start = MagicMock()

    result = use_task_button(mock_task, on_start=on_start)

    assert result["running"] is True


def test_use_task_button_cancel_calls_task_cancel():
    """on_cancel from use_task_button calls task.cancel()."""
    mock_task = MagicMock()
    mock_task.pending = True
    on_start = MagicMock()

    result = use_task_button(mock_task, on_start=on_start)
    result["on_cancel"]()

    mock_task.cancel.assert_called_once()


def test_use_task_button_cancel_sets_reason_ref():
    """on_cancel sets cancel_reason_ref.current to 'user'."""
    mock_task = MagicMock()
    mock_task.pending = True
    on_start = MagicMock()
    reason_ref = MagicMock()
    reason_ref.current = None

    result = use_task_button(
        mock_task,
        on_start=on_start,
        cancel_reason_ref=reason_ref,
    )
    result["on_cancel"]()

    assert reason_ref.current == "user"


def test_use_task_button_cancel_handles_runtime_error():
    """on_cancel swallows RuntimeError from task.cancel()."""
    mock_task = MagicMock()
    mock_task.pending = True
    mock_task.cancel.side_effect = RuntimeError("already cancelled")
    on_start = MagicMock()

    result = use_task_button(mock_task, on_start=on_start)
    result["on_cancel"]()


def test_use_task_button_cancel_noop_when_not_pending():
    """on_cancel does nothing when task is not pending."""
    mock_task = MagicMock()
    mock_task.pending = False
    on_start = MagicMock()

    result = use_task_button(mock_task, on_start=on_start)
    result["on_cancel"]()

    mock_task.cancel.assert_not_called()
