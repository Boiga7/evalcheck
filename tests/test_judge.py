"""Tests for the LLM judge runner."""

import json

import pytest
import respx
from httpx import Response

from evalcheck.judge import (
    AnthropicJudge,
    JudgeResponse,
    OllamaJudge,
    OpenAIJudge,
    make_judge,
)


def _openai_response_payload(content: str) -> dict:
    return {
        "id": "chatcmpl-x",
        "object": "chat.completion",
        "created": 0,
        "model": "gpt-4o-mini",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
    }


def _anthropic_response_payload(content: str) -> dict:
    return {
        "id": "msg_x",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": content}],
        "model": "claude-haiku-4-5",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": 10, "output_tokens": 10},
    }


@respx.mock
def test_openai_judge_returns_parsed_score():
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=Response(
            200,
            json=_openai_response_payload(
                json.dumps({"score": 0.85, "reasoning": "good match"})
            ),
        )
    )

    judge = OpenAIJudge(model="gpt-4o-mini", api_key="sk-test")
    response = judge.score(system="You are an evaluator", user="Score this")

    assert isinstance(response, JudgeResponse)
    assert response.score == 0.85
    assert response.reasoning == "good match"


@respx.mock
def test_openai_judge_handles_missing_reasoning_field():
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=Response(
            200, json=_openai_response_payload(json.dumps({"score": 0.5}))
        )
    )

    judge = OpenAIJudge(api_key="sk-test")
    response = judge.score(system="x", user="y")

    assert response.score == 0.5
    assert response.reasoning is None


@respx.mock
def test_openai_judge_clamps_score_to_unit_interval():
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=Response(
            200, json=_openai_response_payload(json.dumps({"score": 1.5}))
        )
    )

    judge = OpenAIJudge(api_key="sk-test")
    response = judge.score(system="x", user="y")

    assert response.score == 1.0


@respx.mock
def test_anthropic_judge_returns_parsed_score():
    respx.post("https://api.anthropic.com/v1/messages").mock(
        return_value=Response(
            200,
            json=_anthropic_response_payload(
                json.dumps({"score": 0.72, "reasoning": "partial"})
            ),
        )
    )

    judge = AnthropicJudge(model="claude-haiku-4-5", api_key="sk-ant-test")
    response = judge.score(system="evaluator", user="score this")

    assert response.score == 0.72
    assert response.reasoning == "partial"


def test_make_judge_parses_openai_spec():
    judge = make_judge("openai:gpt-4o-mini", api_key="sk-test")
    assert isinstance(judge, OpenAIJudge)


def test_make_judge_parses_anthropic_spec():
    judge = make_judge("anthropic:claude-haiku-4-5", api_key="sk-ant-test")
    assert isinstance(judge, AnthropicJudge)


def test_make_judge_rejects_unknown_provider():
    with pytest.raises(ValueError, match="unknown provider"):
        make_judge("vertex:gemini-flash")


def test_make_judge_reads_env_var_when_no_spec(monkeypatch):
    monkeypatch.setenv("EVALCHECK_JUDGE_MODEL", "anthropic:claude-haiku-4-5")
    judge = make_judge(api_key="sk-ant-test")
    assert isinstance(judge, AnthropicJudge)


@respx.mock
def test_ollama_judge_returns_parsed_score():
    respx.post("http://localhost:11434/v1/chat/completions").mock(
        return_value=Response(
            200,
            json=_openai_response_payload(
                json.dumps({"score": 0.6, "reasoning": "local model said so"})
            ),
        )
    )

    judge = OllamaJudge(model="llama3.2:3b")
    response = judge.score(system="evaluator", user="score this")

    assert response.score == 0.6
    assert response.reasoning == "local model said so"


@respx.mock
def test_ollama_judge_uses_custom_host(monkeypatch):
    monkeypatch.setenv("EVALCHECK_OLLAMA_HOST", "http://remote-ollama:8080")
    respx.post("http://remote-ollama:8080/v1/chat/completions").mock(
        return_value=Response(
            200, json=_openai_response_payload(json.dumps({"score": 0.4}))
        )
    )

    judge = OllamaJudge()
    response = judge.score(system="x", user="y")

    assert response.score == 0.4


def test_make_judge_parses_ollama_spec():
    judge = make_judge("ollama:llama3.2:3b")
    assert isinstance(judge, OllamaJudge)


def test_openai_judge_raises_install_hint_when_sdk_missing(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "openai", None)
    with pytest.raises(ImportError, match="evalcheck\\[openai\\]"):
        OpenAIJudge(api_key="sk-test")


def test_anthropic_judge_raises_install_hint_when_sdk_missing(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "anthropic", None)
    with pytest.raises(ImportError, match="evalcheck\\[anthropic\\]"):
        AnthropicJudge(api_key="sk-ant-test")


def test_ollama_judge_raises_install_hint_when_sdk_missing(monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "openai", None)
    with pytest.raises(ImportError, match="evalcheck\\[openai\\]"):
        OllamaJudge()
