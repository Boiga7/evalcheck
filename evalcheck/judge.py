"""LLM-as-judge runner — provider-agnostic interface plus OpenAI and
Anthropic adapters.

The shape we want from any judge: pass it a system prompt and a user
prompt, get back a score in [0, 1]. We ask the model to return JSON with
{score, reasoning} so the score is parseable and the reasoning is there
for diagnostics. temperature=0 to keep scores stable across runs — vital
because regression detection is otherwise just noise vs noise.
"""

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class JudgeResponse:
    score: float
    reasoning: str | None = None


class Judge(Protocol):
    """Anything with a `score(system, user) -> JudgeResponse` method qualifies.

    Users can pass their own judge implementation via `judge=` on a metric
    if they want to swap providers, mock for tests, or wrap an internal
    LLM gateway.
    """
    def score(self, system: str, user: str) -> JudgeResponse: ...


def _parse_judge_payload(text: str) -> JudgeResponse:
    """Models occasionally hand back scores outside [0, 1] — clamp instead
    of failing the test, since a clamp is closer to user intent than an
    explosion mid-suite.
    """
    data = json.loads(text)
    raw_score = float(data["score"])
    clamped = max(0.0, min(1.0, raw_score))
    return JudgeResponse(score=clamped, reasoning=data.get("reasoning"))


class OpenAIJudge:
    """OpenAI-backed judge. Lazy import of the openai package so users who
    only want the deterministic metrics (or only Anthropic) don't have to
    install OpenAI's SDK.
    """

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
            # Forces JSON output instead of relying on the system prompt
            # alone. Newer models honour the prompt fine, older ones drift.
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content or ""
        return _parse_judge_payload(content)


class OllamaJudge:
    """Local-first judge backed by Ollama's OpenAI-compatible endpoint.

    Ollama exposes `/v1` at `http://localhost:11434` with the same wire
    shape as OpenAI's chat.completions API, so we just point the OpenAI
    SDK at it. No API key required for local inference; the SDK still
    insists on a non-empty value, so we pass a placeholder.

    Set `EVALCHECK_OLLAMA_HOST` to talk to a remote Ollama instance.
    """

    def __init__(
        self, model: str = "llama3.2:3b", host: str | None = None
    ):
        try:
            from openai import OpenAI
        except ImportError as e:
            raise ImportError(
                "OllamaJudge requires the openai package (Ollama uses the "
                "OpenAI wire format). Install with: pip install evalcheck[openai]"
            ) from e
        resolved_host = host or os.environ.get(
            "EVALCHECK_OLLAMA_HOST", "http://localhost:11434"
        )
        # api_key="ollama" is a placeholder; Ollama ignores auth but the
        # OpenAI SDK refuses to construct a client without one.
        self._client = OpenAI(base_url=f"{resolved_host}/v1", api_key="ollama")
        self._model = model

    def score(self, system: str, user: str) -> JudgeResponse:
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0,
            # Ollama's response_format support is patchy across models;
            # we lean on the system prompt to coax JSON instead.
        )
        content = completion.choices[0].message.content or ""
        return _parse_judge_payload(content)


class AnthropicJudge:
    """Anthropic-backed judge. Same shape as OpenAIJudge."""

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
        # Anthropic responses are a list of content blocks. We assume the
        # judge returns a single text block; concatenate just in case the
        # model ever splits its response.
        text = "".join(
            block.text for block in message.content if hasattr(block, "text")
        )
        return _parse_judge_payload(text)


def make_judge(spec: str | None = None, **kwargs: Any) -> Judge:
    """Factory that picks a provider from a `provider:model` string.

    Users normally don't call this directly — built-in metrics call it
    when no `judge=` was passed via the decorator. The env var lets
    teams swap models project-wide without editing every test.
    """
    spec = spec or os.environ.get("EVALCHECK_JUDGE_MODEL", "openai:gpt-4o-mini")
    provider, _, model = spec.partition(":")
    if provider == "openai":
        return OpenAIJudge(model=model or "gpt-4o-mini", **kwargs)
    if provider == "anthropic":
        return AnthropicJudge(model=model or "claude-haiku-4-5", **kwargs)
    if provider == "ollama":
        # Ollama doesn't take an api_key, drop it before forwarding so we
        # don't accidentally pass a stray OpenAI key as a host.
        kwargs.pop("api_key", None)
        return OllamaJudge(model=model or "llama3.2:3b", **kwargs)
    raise ValueError(f"unknown provider: {provider}")
