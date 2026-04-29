"""Deterministic metrics — same inputs always produce the same score.

No LLM call, no flakiness, no API key required. Use these when the
"correct" answer is structural (exact equality, regex pattern) rather
than semantic. For semantic correctness, see `judge_metrics`.
"""

import re


def exact_match(output: str, expected: str) -> float:
    """Returns 1.0 iff the two strings are identical, else 0.0.

    Whitespace and case both matter. Wrap in `output.strip().lower()`
    upstream if you want loose comparison; we don't do it for you so
    the metric stays predictable.
    """
    return 1.0 if output == expected else 0.0


def regex_match(output: str, pattern: str, full_match: bool = False) -> float:
    """1.0 if the regex matches the output, else 0.0.

    `full_match=False` (default) uses re.search — pattern matches any
    substring. `full_match=True` requires the regex to match the entire
    output start-to-end. Use full_match for shape checks like
    `^\\d{4}-\\d{2}-\\d{2}$`; default search for "contains a SKU".
    """
    if full_match:
        return 1.0 if re.fullmatch(pattern, output) else 0.0
    return 1.0 if re.search(pattern, output) else 0.0
