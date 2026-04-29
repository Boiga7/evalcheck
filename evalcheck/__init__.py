"""evalcheck — PR comments for LLM eval regressions.

Public API surface: the `@eval` decorator, the `EvalOutput` return type,
and the six built-in metrics. Everything else (judge, snapshot, runtime,
plugin hooks) is implementation detail accessed via the pytest plugin
machinery, not directly imported by users.
"""

from evalcheck.decorator import eval
from evalcheck.metrics import (
    correctness,
    exact_match,
    faithfulness,
    regex_match,
    relevance,
)
from evalcheck.types import EvalOutput

__version__ = "0.2.0"

__all__ = [
    "EvalOutput",
    "correctness",
    "eval",
    "exact_match",
    "faithfulness",
    "regex_match",
    "relevance",
]
