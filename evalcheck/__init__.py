"""evalcheck — PR comments for LLM eval regressions."""

from evalcheck.decorator import eval
from evalcheck.metrics import (
    correctness,
    exact_match,
    faithfulness,
    regex_match,
    relevance,
)
from evalcheck.types import EvalOutput

__version__ = "0.1.0"

__all__ = [
    "EvalOutput",
    "correctness",
    "eval",
    "exact_match",
    "faithfulness",
    "regex_match",
    "relevance",
]
