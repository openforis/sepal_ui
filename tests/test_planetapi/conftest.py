"""Auto-retry transient failures from Planet's live API.

Tests in this directory hit api.planet.com and are subject to rate-limiting
(HTTP 429) and transient connection errors. We retry only those — real
assertion failures and other exceptions still fail fast on the first run.
"""

import pytest

_RERUN_ON = (
    # pytest-rerunfailures regex-matches these against the failure repr
    # (e.g. "TooManyRequests(...)"), so use bare class names.
    "TooManyRequests",
    "TooManyRedirects",
    "ConnectError",
    "ReadTimeout",
    "RemoteProtocolError",
    "ConnectionError",
    "ServerError",
)


def pytest_collection_modifyitems(config, items):
    """Attach a flaky marker to every test under tests/test_planetapi/."""
    marker = pytest.mark.flaky(
        reruns=3,
        reruns_delay=15,
        only_rerun=list(_RERUN_ON),
    )
    for item in items:
        if "test_planetapi" in item.nodeid:
            item.add_marker(marker)
