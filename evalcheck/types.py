"""Public dataclasses for evalcheck."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvalOutput:
    output: str
    input: str | None = None
    context: str | None = None
    expected: str | None = None
    metadata: dict[str, Any] | None = None
