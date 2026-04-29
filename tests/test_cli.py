"""Tests for the evalcheck CLI."""

import json

import pytest

from evalcheck.cli import main
from evalcheck.snapshot import Snapshot, save_results


def _seed_results(path):
    save_results(
        path,
        [
            Snapshot(
                test_id="tests/test_x.py::test_a",
                metric="faithfulness",
                score=0.85,
                threshold=0.7,
                timestamp="2026-04-29T11:00:00Z",
            ),
            Snapshot(
                test_id="tests/test_x.py::test_b",
                metric="exact_match",
                score=1.0,
                threshold=1.0,
                timestamp="2026-04-29T11:00:00Z",
            ),
        ],
    )


def test_snapshot_update_copies_results_to_baseline(tmp_path, monkeypatch):
    results = tmp_path / ".evalcheck" / "results.json"
    _seed_results(results)
    monkeypatch.chdir(tmp_path)

    exit_code = main(["snapshot", "--update"])

    assert exit_code == 0
    baseline = tmp_path / ".evalcheck" / "snapshots" / "baseline.json"
    assert baseline.exists()

    data = json.loads(baseline.read_text())
    assert data["schema_version"] == 1
    assert len(data["runs"]) == 2


def test_snapshot_update_returns_nonzero_when_results_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    exit_code = main(["snapshot", "--update"])
    assert exit_code != 0


def test_snapshot_update_accepts_custom_paths(tmp_path):
    custom_results = tmp_path / "out" / "my-results.json"
    custom_baseline = tmp_path / "snap" / "my-baseline.json"
    _seed_results(custom_results)

    exit_code = main(
        [
            "snapshot",
            "--update",
            "--results",
            str(custom_results),
            "--baseline",
            str(custom_baseline),
        ]
    )

    assert exit_code == 0
    assert custom_baseline.exists()


def test_cli_with_no_args_returns_nonzero():
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code != 0


def test_cli_snapshot_without_update_errors():
    with pytest.raises(SystemExit) as exc_info:
        main(["snapshot"])
    assert exc_info.value.code != 0
