"""Per-pytest-session result accumulator.

Decorator wrappers `record()` here as they run; the plugin's
`pytest_sessionfinish` hook reads them all out and writes results.json.
A module-level list is fine for this — pytest sessions are single-process
and we reset on `pytest_sessionstart` so leftover state from a previous
run can't pollute.

If we ever support `pytest-xdist` parallel workers writing to the same
results.json, this will need replacing with a file-based aggregator.
For now xdist works fine because each worker writes its own file path
and the GitHub App reads them all from the artifact.
"""

from datetime import datetime, timezone

from evalcheck.snapshot import Snapshot

_results: list[Snapshot] = []


def record(
    test_id: str, metric: str, score: float, threshold: float | None
) -> None:
    """Append one Snapshot. Timestamps are recorded in UTC ISO 8601 since
    that's what the GitHub App and downstream tools expect.
    """
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
    """Return a copy so callers can't mutate the internal list. Cheap; the
    list is at most a few hundred items in any realistic suite.
    """
    return list(_results)


def reset() -> None:
    """Called from `pytest_sessionstart`. Clears state from any previous
    in-process pytest run — relevant during pytester self-tests or when
    pytest is invoked programmatically.
    """
    _results.clear()
