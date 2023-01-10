"""
Parameters of the reclassification interface.
"""

from sepal_ui.message import ms

__all__ = ["MATRIX_NAMES", "TABLE_NAMES", "NO_VALUE", "SCHEMA"]

MATRIX_NAMES: list = ["src", "dst"]
TABLE_NAMES: list = ["code", "desc", "color"]

# Set a value for missing reclassifications
NO_VALUE: int = 999

SCHEMA: dict = {
    "id": [ms.rec.table.schema.id, "number"],
    "code": [ms.rec.table.schema.code, "number"],
    "desc": [ms.rec.table.schema.description, "string"],
    "color": [ms.rec.table.schema.color, "hexa"],
}
