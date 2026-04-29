"""Tests for the per-session results accumulator."""

import pytest

from evalcheck import runtime


@pytest.fixture(autouse=True)
def _reset():
    runtime.reset()
    yield
    runtime.reset()


def test_record_appends_a_snapshot():
    runtime.record(
        test_id="t::a", metric="exact_match", score=1.0, threshold=1.0
    )
    results = runtime.collected_results()
    assert len(results) == 1
    assert results[0].test_id == "t::a"
    assert results[0].metric == "exact_match"
    assert results[0].score == 1.0
    assert results[0].threshold == 1.0
    assert results[0].timestamp.endswith("+00:00") or results[0].timestamp.endswith("Z")


def test_record_accumulates_across_calls():
    runtime.record(test_id="t::a", metric="m1", score=1.0, threshold=None)
    runtime.record(test_id="t::b", metric="m2", score=0.5, threshold=0.4)
    assert len(runtime.collected_results()) == 2


def test_reset_clears_accumulator():
    runtime.record(test_id="t::a", metric="m1", score=1.0, threshold=None)
    runtime.reset()
    assert runtime.collected_results() == []


def test_collected_results_returns_a_copy():
    runtime.record(test_id="t::a", metric="m1", score=1.0, threshold=None)
    snapshot = runtime.collected_results()
    snapshot.clear()
    assert len(runtime.collected_results()) == 1
