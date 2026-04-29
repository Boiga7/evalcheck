"""Snapshot file format — git-committed JSON for regression baselines.

`baseline.json` is what users commit; `results.json` is what each pytest
run writes. Same schema so the GitHub App can `cp results.json
baseline.json` to bless a run, and the plugin can read either one back
without caring which it's looking at.

schema_version exists so a future change can add fields without breaking
old baselines silently. Bump it when the on-disk format changes.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

SCHEMA_VERSION = 1


@dataclass
class Snapshot:
    test_id: str
    metric: str
    score: float
    threshold: float | None
    timestamp: str


def load_baseline(path: Path) -> dict[tuple[str, str], float]:
    """Read a baseline file as a dict keyed on (test_id, metric).

    Returns an empty dict if the file doesn't exist — that's the normal
    "first run on a project" case, not an error. Callers use the dict
    membership check to decide whether a regression check applies.
    """
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    schema = data.get("schema_version")
    if schema != SCHEMA_VERSION:
        # Don't try to migrate. If we ever ship v2, write a one-time
        # migration helper. For now an explicit error is safer than
        # silent score drift.
        raise ValueError(
            f"unsupported schema_version: {schema} (expected {SCHEMA_VERSION})"
        )
    return {(run["test_id"], run["metric"]): run["score"] for run in data["runs"]}


def save_results(path: Path, snapshots: list[Snapshot]) -> None:
    """Write a list of snapshots to disk in the canonical format.

    Creates the parent directory if needed — saves users a `mkdir -p`.
    `indent=2` keeps the file diff-friendly when committed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "runs": [asdict(s) for s in snapshots],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
