"""Tests for judge-based metrics: faithfulness, relevance, correctness."""

from evalcheck import correctness, faithfulness, relevance
from evalcheck.judge import JudgeResponse


class FakeJudge:
    def __init__(self, score: float = 0.5, reasoning: str | None = None):
        self.score_value = score
        self.reasoning = reasoning
        self.last_system: str | None = None
        self.last_user: str | None = None

    def score(self, system: str, user: str) -> JudgeResponse:
        self.last_system = system
        self.last_user = user
        return JudgeResponse(score=self.score_value, reasoning=self.reasoning)


def test_faithfulness_returns_judge_score():
    judge = FakeJudge(score=0.9)
    result = faithfulness(
        output="Paris is the capital of France.",
        context="France's capital is Paris.",
        judge=judge,
    )
    assert result == 0.9


def test_faithfulness_includes_output_and_context_in_prompt():
    judge = FakeJudge(score=1.0)
    faithfulness(
        output="THE-OUTPUT-MARKER",
        context="THE-CONTEXT-MARKER",
        judge=judge,
    )
    assert "THE-OUTPUT-MARKER" in judge.last_user
    assert "THE-CONTEXT-MARKER" in judge.last_user


def test_relevance_returns_judge_score():
    judge = FakeJudge(score=0.8)
    result = relevance(
        output="Paris.",
        input="What is the capital of France?",
        judge=judge,
    )
    assert result == 0.8


def test_relevance_includes_input_and_output_in_prompt():
    judge = FakeJudge(score=1.0)
    relevance(
        output="THE-OUTPUT-MARKER",
        input="THE-INPUT-MARKER",
        judge=judge,
    )
    assert "THE-OUTPUT-MARKER" in judge.last_user
    assert "THE-INPUT-MARKER" in judge.last_user


def test_correctness_returns_judge_score():
    judge = FakeJudge(score=0.75)
    result = correctness(
        output="Paris",
        expected="Paris, France",
        judge=judge,
    )
    assert result == 0.75


def test_correctness_includes_output_and_expected_in_prompt():
    judge = FakeJudge(score=1.0)
    correctness(
        output="THE-OUTPUT-MARKER",
        expected="THE-EXPECTED-MARKER",
        judge=judge,
    )
    assert "THE-OUTPUT-MARKER" in judge.last_user
    assert "THE-EXPECTED-MARKER" in judge.last_user


def test_judge_metric_works_through_eval_decorator():
    from evalcheck import EvalOutput, eval

    judge = FakeJudge(score=0.95)

    @eval(faithfulness, threshold=0.9, judge=judge)
    def fake_test():
        return EvalOutput(
            output="Paris is the capital.",
            context="The capital of France is Paris.",
        )

    fake_test()  # should not raise; judge returns 0.95 ≥ 0.9


def test_judge_metric_with_baseline_regression_raises(tmp_path):
    """Weekend 2 acceptance: judge call + baseline diff in one flow."""
    import pytest
    from evalcheck import EvalOutput, eval
    from evalcheck.snapshot import Snapshot, save_results

    baseline = tmp_path / "baseline.json"
    save_results(
        baseline,
        [
            Snapshot(
                test_id="my_test",
                metric="faithfulness",
                score=0.85,
                threshold=None,
                timestamp="2026-04-29T10:00:00Z",
            )
        ],
    )

    judge = FakeJudge(score=0.6)  # dropped from 0.85

    @eval(
        faithfulness,
        judge=judge,
        baseline_path=baseline,
        test_id="my_test",
        regression_tolerance=0.05,
    )
    def fake_test():
        return EvalOutput(output="some output", context="some context")

    with pytest.raises(AssertionError, match="regression"):
        fake_test()
