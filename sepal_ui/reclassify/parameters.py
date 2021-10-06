from sepal_ui.message import ms

__all__ = ["MATRIX_NAMES", "TABLE_NAMES", "NO_VALUE", "SCHEMA"]

MATRIX_NAMES = ["src", "dst"]
TABLE_NAMES = ["code", "desc", "color"]

# Set a value for missing reclassifications
NO_VALUE = 999

SCHEMA = {
    "id": [ms.rec.table.schema.id, "number"],
    "code": [ms.rec.table.schema.code, "number"],
    "desc": [ms.rec.table.schema.description, "string"],
    "color": [ms.rec.table.schema.color, "hexa"],
}
