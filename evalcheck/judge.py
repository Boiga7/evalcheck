"""LLM judge runner — provider abstraction for OpenAI and Anthropic."""

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class JudgeResponse:
    score: float
    reasoning: str | None = None


class Judge(Protocol):
    def score(self, system: str, user: str) -> JudgeResponse: ...


def _parse_judge_payload(text: str) -> JudgeResponse:
    data = json.loads(text)
    raw_score = float(data["score"])
    clamped = max(0.0, min(1.0, raw_score))
    return JudgeResponse(score=clamped, reasoning=data.get("reasoning"))


class OpenAIJudge:
    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None):
        try:
            from openai import OpenAI
        except ImportError as e:
            raise ImportError(
                "OpenAIJudge requires the openai package. "
                "Install with: pip install evalcheck[openai]"
            ) from e
        self._client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        self._model = model

    def score(self, system: str, user: str) -> JudgeResponse:
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content or ""
        return _parse_judge_payload(content)


class AnthropicJudge:
    def __init__(
        self, model: str = "claude-haiku-4-5", api_key: str | None = None
    ):
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise ImportError(
                "AnthropicJudge requires the anthropic package. "
                "Install with: pip install evalcheck[anthropic]"
            ) from e
        self._client = Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self._model = model

    def score(self, system: str, user: str) -> JudgeResponse:
        message = self._client.messages.create(
            model=self._model,
            system=system,
            max_tokens=1024,
            temperature=0,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(
            block.text for block in message.content if hasattr(block, "text")
        )
        return _parse_judge_payload(text)


def make_judge(spec: str | None = None, **kwargs: Any) -> Judge:
    spec = spec or os.environ.get("EVALCHECK_JUDGE_MODEL", "openai:gpt-4o-mini")
    provider, _, model = spec.partition(":")
    if provider == "openai":
        return OpenAIJudge(model=model or "gpt-4o-mini", **kwargs)
    if provider == "anthropic":
        return AnthropicJudge(model=model or "claude-haiku-4-5", **kwargs)
    raise ValueError(f"unknown provider: {provider}")
