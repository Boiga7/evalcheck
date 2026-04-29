"""evalcheck command-line interface.

One subcommand for now: `evalcheck snapshot --update`, which copies
the latest results.json over the committed baseline.json. The user
then commits the new baseline. That's the whole "bless this run"
ceremony — no DB, no API call, just a file move.
"""

import argparse
import shutil
import sys
from pathlib import Path

DEFAULT_RESULTS = Path(".evalcheck/results.json")
DEFAULT_BASELINE = Path(".evalcheck/snapshots/baseline.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="evalcheck")
    sub = parser.add_subparsers(dest="command", required=True)

    snap = sub.add_parser("snapshot", help="manage baseline snapshots")
    snap.add_argument(
        "--update",
        action="store_true",
        help="bless results.json as the new baseline",
    )
    snap.add_argument("--results", default=DEFAULT_RESULTS, type=Path)
    snap.add_argument("--baseline", default=DEFAULT_BASELINE, type=Path)

    args = parser.parse_args(argv)

    if args.command == "snapshot" and args.update:
        return _snapshot_update(args.results, args.baseline)

    # Currently `snapshot` without `--update` has nothing to do. snap.error
    # exits with the right usage hint instead of returning silently — keeps
    # the CLI honest about which combinations actually do work.
    snap.error("snapshot requires --update (no other actions implemented)")


def _snapshot_update(results: Path, baseline: Path) -> int:
    if not results.exists():
        print(f"no results found at {results}", file=sys.stderr)
        return 1
    baseline.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(results, baseline)
    print(f"baseline updated: {results} -> {baseline}")
    return 0
