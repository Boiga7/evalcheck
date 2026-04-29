"""Deterministic metrics — no LLM calls, fully reproducible."""

import re


def exact_match(output: str, expected: str) -> float:
    return 1.0 if output == expected else 0.0


def regex_match(output: str, pattern: str, full_match: bool = False) -> float:
    if full_match:
        return 1.0 if re.fullmatch(pattern, output) else 0.0
    return 1.0 if re.search(pattern, output) else 0.0
