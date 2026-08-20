"""A catalog key must not shadow a dict attribute.

``Translator`` subclasses ``Box`` subclasses ``dict``, so ``cm.buttons.clear``
returns ``dict.clear`` -- a bound method -- rather than the translated string,
with no error anywhere. It reaches the UI as
``<bound method Box.clear of Box({...})>``.
"""

import json
from pathlib import Path

import pytest

import pysepal

REPO_ROOT = Path(pysepal.__file__).parent.parent

CATALOGS = sorted(
    path
    for root in (Path(pysepal.__file__).parent, REPO_ROOT / "demo_apps")
    if root.is_dir()
    for path in root.rglob("message/**/*.json")
)

SHADOWED = frozenset(dir(dict))


def _keys(node, prefix=""):
    """Yield every dotted key path in a catalog."""
    for key, value in node.items():
        yield f"{prefix}{key}"
        if isinstance(value, dict):
            yield from _keys(value, f"{prefix}{key}.")


def test_catalogs_are_discovered():
    """Guard the guard: a bad glob would make the check below vacuous."""
    assert CATALOGS


@pytest.mark.parametrize("path", CATALOGS, ids=lambda p: f"{p.parent.name}/{p.name}")
def test_no_key_shadows_a_dict_attribute(path: Path):
    clashing = [
        key for key in _keys(json.loads(path.read_text())) if key.split(".")[-1] in SHADOWED
    ]
    assert clashing == [], (
        f"{path} uses {clashing}, which dict already defines. Attribute access "
        "returns the method, not the translation. Rename the key."
    )
