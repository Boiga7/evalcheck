"""Tests for the pytest plugin's session hooks."""

import json


def test_results_json_is_written_at_session_end(pytester, monkeypatch):
    monkeypatch.setenv("EVALCHECK_AUTOWRITE", "1")
    pytester.makepyfile(
        """
        from evalcheck import EvalOutput, eval, exact_match

        @eval(exact_match, threshold=1.0)
        def test_passes():
            return EvalOutput(output="hi", expected="hi")

        @eval(exact_match, threshold=1.0)
        def test_fails():
            return EvalOutput(output="hi", expected="bye")
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1, failed=1)

    results_file = pytester.path / ".evalcheck" / "results.json"
    assert results_file.exists()

    data = json.loads(results_file.read_text())
    assert data["schema_version"] == 1
    assert len(data["runs"]) == 2

    by_test = {run["test_id"]: run for run in data["runs"]}
    passing = next(v for k, v in by_test.items() if "test_passes" in k)
    failing = next(v for k, v in by_test.items() if "test_fails" in k)
    assert passing["score"] == 1.0
    assert failing["score"] == 0.0


def test_results_json_not_written_when_autowrite_disabled(pytester, monkeypatch):
    monkeypatch.setenv("EVALCHECK_AUTOWRITE", "0")
    pytester.makepyfile(
        """
        from evalcheck import EvalOutput, eval, exact_match

        @eval(exact_match, threshold=1.0)
        def test_x():
            return EvalOutput(output="hi", expected="hi")
        """
    )
    pytester.runpytest()
    assert not (pytester.path / ".evalcheck" / "results.json").exists()


def test_results_json_not_written_when_no_evals_recorded(pytester, monkeypatch):
    monkeypatch.setenv("EVALCHECK_AUTOWRITE", "1")
    pytester.makepyfile(
        """
        def test_just_a_normal_test():
            assert 1 + 1 == 2
        """
    )
    pytester.runpytest()
    assert not (pytester.path / ".evalcheck" / "results.json").exists()
