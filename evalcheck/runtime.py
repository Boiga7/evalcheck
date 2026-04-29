"""Per-session result accumulator. Cleared at session start, written at session end."""

from datetime import datetime, timezone

from evalcheck.snapshot import Snapshot

_results: list[Snapshot] = []


def record(
    test_id: str, metric: str, score: float, threshold: float | None
) -> None:
    _results.append(
        Snapshot(
            test_id=test_id,
            metric=metric,
            score=score,
            threshold=threshold,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    )


def collected_results() -> list[Snapshot]:
    return list(_results)


def reset() -> None:
    _results.clear()
