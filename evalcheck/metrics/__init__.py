"""Built-in metrics for evalcheck.

Two families:
  - deterministic: exact_match, regex_match. No LLM call, fully reproducible.
  - judge-based: faithfulness, relevance, correctness. Use an LLM judge.

Users can also write custom metrics by passing any callable returning a
float in [0, 1] to `@eval(metric=my_fn, ...)`.
"""

from evalcheck.metrics.deterministic import exact_match, regex_match
from evalcheck.metrics.judge_metrics import correctness, faithfulness, relevance

__all__ = [
    "correctness",
    "exact_match",
    "faithfulness",
    "regex_match",
    "relevance",
]
