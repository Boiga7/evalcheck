"""Public dataclasses returned from @eval-decorated tests.

EvalOutput is what tests hand back when a metric needs more than the
output string — `context` for faithfulness, `expected` for correctness,
`input` for relevance. Tests can also return a plain string when the
metric only needs that, and the decorator wraps it for them.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class EvalOutput:
    output: str
    # The user input / question, for relevance-style metrics.
    input: str | None = None
    # The retrieved context (RAG), for faithfulness-style metrics.
    context: str | None = None
    # The desired answer, for exact_match / correctness.
    expected: str | None = None
    # Free-form bag for things we don't model directly: latency, cost,
    # token counts, model name, etc. Not interpreted by built-in metrics
    # but available to custom ones.
    metadata: dict[str, Any] | None = None
