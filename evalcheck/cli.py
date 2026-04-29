"""evalcheck CLI."""

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

    snap.error("snapshot requires --update (no other actions implemented)")


def _snapshot_update(results: Path, baseline: Path) -> int:
    if not results.exists():
        print(f"no results found at {results}", file=sys.stderr)
        return 1
    baseline.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(results, baseline)
    print(f"baseline updated: {results} -> {baseline}")
    return 0
