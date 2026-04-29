"""Tests for the EvalOutput dataclass."""

from evalcheck import EvalOutput


def test_eval_output_holds_just_an_output_string():
    result = EvalOutput(output="hello")
    assert result.output == "hello"
    assert result.context is None
    assert result.expected is None
    assert result.input is None
    assert result.metadata is None


def test_eval_output_holds_input_for_relevance_metrics():
    result = EvalOutput(output="Paris", input="What is the capital of France?")
    assert result.input == "What is the capital of France?"


def test_eval_output_holds_context_and_expected():
    result = EvalOutput(
        output="The capital of France is Paris.",
        context="France's capital city is Paris, located on the Seine.",
        expected="Paris",
    )
    assert result.context.startswith("France's capital")
    assert result.expected == "Paris"


def test_eval_output_metadata_is_arbitrary_dict():
    result = EvalOutput(output="x", metadata={"latency_ms": 240, "tokens": 18})
    assert result.metadata["latency_ms"] == 240
    assert result.metadata["tokens"] == 18


def test_eval_output_equality():
    a = EvalOutput(output="hi", expected="hi")
    b = EvalOutput(output="hi", expected="hi")
    assert a == b
