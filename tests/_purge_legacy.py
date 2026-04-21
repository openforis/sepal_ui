"""One-time purge of legacy stale test assets at project root.

This script targets the pre-container layout: folders matching
`projects/<project>/assets/sepal-ui-*` at the assets root (NOT inside
`pysepal-tests/`). After Task 5, new sessions create their folders inside
the container, but any folders created before that still live at the root.

Usage:
    python -m tests._purge_legacy           # dry-run
    python -m tests._purge_legacy --yes     # actually delete

After running once with --yes, delete this file in a follow-up commit.
"""

from __future__ import annotations

import argparse
import sys

import ee


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yes", action="store_true", help="Actually delete.")
    args = parser.parse_args(argv)

    if not ee.data.is_initialized():
        ee.Initialize()

    project_id = ee.data.getProjectConfig()["name"].split("/")[1]
    root = f"projects/{project_id}/assets"
    response = ee.data.listAssets({"parent": root})
    targets = [
        a["name"]
        for a in response.get("assets", [])
        if a["name"].rsplit("/", 1)[-1].startswith("sepal-ui-")
    ]

    if not targets:
        print("No legacy stale assets found at project root.")
        return 0

    print(f"Found {len(targets)} legacy folder(s) at project root:")
    for t in targets:
        print(f"  {t}")

    if not args.yes:
        print("\nDry-run. Pass --yes to delete.")
        return 0

    from pysepal.scripts import gee as gee_script

    for t in targets:
        print(f"Deleting {t}...")
        gee_script.delete_assets(t, dry_run=False)

    print(f"Deleted {len(targets)} folder(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
