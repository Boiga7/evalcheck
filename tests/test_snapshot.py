"""Tests for snapshot baselines."""

import json

import pytest

from evalcheck.snapshot import Snapshot, load_baseline, save_results


def test_load_baseline_returns_empty_when_file_missing(tmp_path):
    baseline = load_baseline(tmp_path / "missing.json")
    assert baseline == {}


def test_load_baseline_parses_valid_file(tmp_path):
    path = tmp_path / "baseline.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "runs": [
                    {
                        "test_id": "tests/test_x.py::test_a",
                        "metric": "faithfulness",
                        "score": 0.85,
                        "threshold": 0.7,
                        "timestamp": "2026-04-29T10:00:00Z",
                    },
                    {
                        "test_id": "tests/test_x.py::test_b",
                        "metric": "exact_match",
                        "score": 1.0,
                        "threshold": 1.0,
                        "timestamp": "2026-04-29T10:00:00Z",
                    },
                ],
            }
        )
    )

    baseline = load_baseline(path)

    assert baseline[("tests/test_x.py::test_a", "faithfulness")] == 0.85
    assert baseline[("tests/test_x.py::test_b", "exact_match")] == 1.0


def test_load_baseline_raises_on_unsupported_schema_version(tmp_path):
    path = tmp_path / "baseline.json"
    path.write_text(json.dumps({"schema_version": 999, "runs": []}))

    with pytest.raises(ValueError, match="schema_version"):
        load_baseline(path)


def test_save_results_writes_parseable_json(tmp_path):
    path = tmp_path / "results.json"
    snapshots = [
        Snapshot(
            test_id="tests/test_x.py::test_a",
            metric="faithfulness",
            score=0.92,
            threshold=0.7,
            timestamp="2026-04-29T11:00:00Z",
        ),
    ]

    save_results(path, snapshots)

    data = json.loads(path.read_text())
    assert data["schema_version"] == 1
    assert len(data["runs"]) == 1
    assert data["runs"][0]["test_id"] == "tests/test_x.py::test_a"
    assert data["runs"][0]["score"] == 0.92


def test_save_results_creates_parent_directory(tmp_path):
    path = tmp_path / "nested" / "deep" / "results.json"
    save_results(
        path,
        [
            Snapshot(
                test_id="t",
                metric="m",
                score=1.0,
                threshold=None,
                timestamp="2026-04-29T11:00:00Z",
            )
        ],
    )
    assert path.exists()


def test_round_trip_save_then_load(tmp_path):
    path = tmp_path / "rt.json"
    snapshots = [
        Snapshot(
            test_id="a",
            metric="x",
            score=0.5,
            threshold=0.4,
            timestamp="2026-04-29T11:00:00Z",
        ),
        Snapshot(
            test_id="b",
            metric="y",
            score=0.9,
            threshold=None,
            timestamp="2026-04-29T11:00:00Z",
        ),
    ]
    save_results(path, snapshots)

    baseline = load_baseline(path)
    assert baseline[("a", "x")] == 0.5
    assert baseline[("b", "y")] == 0.9
