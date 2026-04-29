"""Tests for the @eval decorator."""

import pytest

from evalcheck import EvalOutput, eval, exact_match, regex_match, runtime
from evalcheck.snapshot import Snapshot, save_results


@pytest.fixture(autouse=True)
def _reset_runtime():
    runtime.reset()
    yield
    runtime.reset()


def test_eval_decorator_passes_when_score_meets_threshold():
    @eval(exact_match, threshold=1.0)
    def fake_test():
        return EvalOutput(output="hello", expected="hello")

    fake_test()


def test_eval_decorator_raises_when_score_below_threshold():
    @eval(exact_match, threshold=1.0)
    def fake_test():
        return EvalOutput(output="hello", expected="goodbye")

    with pytest.raises(AssertionError):
        fake_test()


def test_eval_decorator_accepts_plain_string_return():
    @eval(exact_match, threshold=1.0, expected="hello")
    def fake_test():
        return "hello"

    fake_test()


def test_eval_decorator_passes_metric_kwargs_through():
    @eval(regex_match, threshold=1.0, pattern=r"#\d+")
    def fake_test():
        return "order #1234 confirmed"

    fake_test()


def test_eval_decorator_rejects_unsupported_return_type():
    @eval(exact_match, threshold=1.0)
    def fake_test():
        return 42

    with pytest.raises(TypeError):
        fake_test()


def test_eval_decorator_with_no_threshold_does_not_raise():
    @eval(exact_match)
    def fake_test():
        return EvalOutput(output="hello", expected="goodbye")

    fake_test()


def test_eval_decorator_exposes_score_via_last_score_attribute():
    @eval(exact_match)
    def fake_test():
        return EvalOutput(output="hi", expected="hi")

    fake_test()
    assert fake_test.last_score == 1.0


def test_eval_decorator_attaches_metadata_to_function():
    @eval(exact_match, threshold=0.8)
    def fake_test():
        return EvalOutput(output="x", expected="x")

    assert fake_test._evalcheck_metric is exact_match
    assert fake_test._evalcheck_threshold == 0.8


def _write_baseline(path, test_id, metric, score):
    save_results(
        path,
        [
            Snapshot(
                test_id=test_id,
                metric=metric,
                score=score,
                threshold=None,
                timestamp="2026-04-29T10:00:00Z",
            )
        ],
    )


def test_eval_decorator_raises_on_regression_below_tolerance(tmp_path):
    baseline = tmp_path / "baseline.json"
    _write_baseline(baseline, test_id="my_test", metric="exact_match", score=0.9)

    @eval(
        exact_match,
        regression_tolerance=0.05,
        baseline_path=baseline,
        test_id="my_test",
    )
    def fake_test():
        return EvalOutput(output="hi", expected="bye")  # score 0.0, baseline 0.9

    with pytest.raises(AssertionError, match="regression"):
        fake_test()


def test_eval_decorator_passes_when_score_within_regression_tolerance(tmp_path):
    baseline = tmp_path / "baseline.json"
    _write_baseline(baseline, test_id="my_test", metric="exact_match", score=1.0)

    @eval(
        exact_match,
        regression_tolerance=0.1,
        baseline_path=baseline,
        test_id="my_test",
    )
    def fake_test():
        return EvalOutput(output="hi", expected="hi")  # score 1.0, baseline 1.0

    fake_test()


def test_eval_decorator_skips_regression_when_no_baseline_entry(tmp_path):
    baseline = tmp_path / "baseline.json"
    _write_baseline(baseline, test_id="other_test", metric="exact_match", score=0.9)

    @eval(
        exact_match,
        regression_tolerance=0.05,
        baseline_path=baseline,
        test_id="my_test",
    )
    def fake_test():
        return EvalOutput(output="hi", expected="bye")  # no baseline for this test_id

    fake_test()


def test_eval_decorator_skips_regression_when_baseline_file_missing(tmp_path):
    @eval(
        exact_match,
        baseline_path=tmp_path / "does-not-exist.json",
        test_id="my_test",
    )
    def fake_test():
        return EvalOutput(output="hi", expected="bye")

    fake_test()  # should not raise — no baseline = no regression check


def test_eval_decorator_records_result_in_runtime():
    @eval(exact_match, threshold=1.0, test_id="recorded_test")
    def fake_test():
        return EvalOutput(output="hi", expected="hi")

    fake_test()

    results = runtime.collected_results()
    assert len(results) == 1
    assert results[0].test_id == "recorded_test"
    assert results[0].metric == "exact_match"
    assert results[0].score == 1.0
    assert results[0].threshold == 1.0


def test_eval_decorator_records_even_when_threshold_fails():
    @eval(exact_match, threshold=1.0, test_id="failing_test")
    def fake_test():
        return EvalOutput(output="hi", expected="bye")

    with pytest.raises(AssertionError):
        fake_test()

    results = runtime.collected_results()
    assert len(results) == 1
    assert results[0].test_id == "failing_test"
    assert results[0].score == 0.0


def test_eval_decorator_falls_back_to_unknown_when_outside_pytest(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    @eval(exact_match)
    def fake_test():
        return EvalOutput(output="hi", expected="hi")

    fake_test()

    results = runtime.collected_results()
    assert results[-1].test_id == "<unknown>"
