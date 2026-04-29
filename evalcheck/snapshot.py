"""Snapshot baselines — JSON-on-disk regression tracking."""

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
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    schema = data.get("schema_version")
    if schema != SCHEMA_VERSION:
        raise ValueError(
            f"unsupported schema_version: {schema} (expected {SCHEMA_VERSION})"
        )
    return {(run["test_id"], run["metric"]): run["score"] for run in data["runs"]}


def save_results(path: Path, snapshots: list[Snapshot]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "runs": [asdict(s) for s in snapshots],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
