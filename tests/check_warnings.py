"""Check the warnings from doc builds."""

import re
import sys
from pathlib import Path

_SEPAL_DEPRECATION_RE = re.compile(r"The 'sepal_ui' package is deprecated")


def _filter_deprecation_blocks(lines: list[str]) -> list[str]:
    """Remove 'Cell printed to stderr' warning blocks caused by the sepal_ui deprecation notice.

    jupyter_sphinx captures kernel stderr and emits it as multi-line Sphinx
    warnings.  Each block starts with ``WARNING: Cell printed to stderr:``
    and continues with indented/empty lines until the next ``WARNING:`` or EOF.
    We drop entire blocks that contain the sepal_ui deprecation message.
    """
    blocks: list[list[str]] = []
    for line in lines:
        if "WARNING:" in line:
            blocks.append([line])
        elif blocks:
            blocks[-1].append(line)

    kept: list[str] = []
    for block in blocks:
        block_text = "\n".join(block)
        if "Cell printed to stderr" in block[0] and _SEPAL_DEPRECATION_RE.search(block_text):
            continue  # drop the entire block
        kept.extend(block)

    return kept


def check_warnings(file: Path) -> int:
    """Check the list of warnings produced by the GitHub CI tests raises errors if there are unexpected ones and/or if some are missing.

    Args:
        file: the path to the generated warning.txt file from
            the CI build

    Returns:
        0 if the warnings are all there
        1 if some warning are not registered or unexpected
    """
    # print some log
    print("\n=== Sphinx Warnings test ===\n")

    # find the file where all the known warnings are stored
    warning_file = Path(__file__).parent / "data" / "warning_list.txt"

    raw_lines = [w for w in file.read_text().strip().split("\n") if w.strip()]
    test_warnings = _filter_deprecation_blocks(raw_lines)
    ref_warnings = warning_file.read_text().strip().split("\n")

    print(
        f'Checking build warnings in file: "{file}" and comparing to expected '
        f'warnings defined in "{warning_file}"\n\n'
    )

    # find all the missing warnings
    missing_warnings = []
    for wa in ref_warnings:
        index = [i for i, twa in enumerate(test_warnings) if wa in twa]
        if len(index) == 0:
            missing_warnings += [wa]
            print(f"Warning was not raised: {wa}\n")
        else:
            test_warnings.pop(index[0])

    # the remaining one are unexpected
    for twa in test_warnings:
        print(f"Unexpected warning: {twa}\n")

    return len(missing_warnings) != 0 or len(test_warnings) != 0


if __name__ == "__main__":

    # cast the file to path and resolve to an absolute one
    file = Path.cwd() / "warnings.txt"

    # execute the test
    sys.exit(check_warnings(file))
