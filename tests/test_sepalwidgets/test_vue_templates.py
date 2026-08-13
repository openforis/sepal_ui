"""ipyvue evaluates a template's ``export default`` object, not its module.

A ``const`` declared beside that object -- the ordinary way to name a constant
in a ``.vue`` file -- is therefore not in scope inside ``methods``, and every
call raises ``ReferenceError``. ``LocaleSelect`` hit exactly this: its
localStorage key lived in a module-level ``const``, so both the read and the
write threw into their ``catch`` blocks and the user's language pick was
silently never persisted.
"""

import re
from pathlib import Path

import pytest

import pysepal

VUE_FILES = sorted((Path(pysepal.__file__).parent).rglob("*.vue"))

#: A binding introduced at the top level of the ``<script>`` block.
DECLARATION = re.compile(r"^(?:const|let|var|function|class)\s+(\w+)", re.MULTILINE)


def _module_scope_source(path: Path) -> str:
    """Return the part of the script that precedes ``export default``."""
    script = path.read_text().partition("<script>")[2]
    return script.partition("export default")[0]


def test_there_are_vue_files_to_check():
    """Guard the guard: a bad glob would make every assertion below vacuous."""
    assert VUE_FILES


@pytest.mark.parametrize("path", VUE_FILES, ids=lambda p: p.name)
def test_no_binding_is_declared_outside_the_exported_object(path: Path):
    declared = DECLARATION.findall(_module_scope_source(path))
    assert declared == [], (
        f"{path.name} declares {declared} beside `export default`. ipyvue does not "
        "evaluate the script as a module, so these are undefined inside methods. "
        "Inline the value, or put it on the exported object."
    )
