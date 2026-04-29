"""The @eval decorator — the single entry point for users.

It wraps a normal pytest function so that:
  1. The function runs as usual and returns either a str or an EvalOutput.
  2. The wrapper calls the metric on the return value.
  3. The wrapper records the result in the runtime accumulator (for the
     plugin's session_finish hook to write to disk).
  4. The wrapper asserts threshold and regression-vs-baseline.

Pytest sees the wrapper, not the original function. So pytest fixtures,
parametrize, xdist, etc. all compose normally.
"""

import functools
import inspect
import os
from pathlib import Path
from typing import Any, Callable

from evalcheck import runtime
from evalcheck.snapshot import load_baseline
from evalcheck.types import EvalOutput

# Where regression baselines live by default. Users can override per
# decorator via baseline_path=, but most won't.
DEFAULT_BASELINE_PATH = Path(".evalcheck/snapshots/baseline.json")


def eval(
    metric: Callable[..., float],
    threshold: float | None = None,
    regression_tolerance: float = 0.05,
    baseline_path: Path | str | None = None,
    test_id: str | None = None,
    **metric_kwargs: Any,
) -> Callable:
    """Decorate a test so its return value is scored against `metric`.

    `regression_tolerance` is the slack we allow vs the baseline before
    failing. 0.05 is generous enough that a single judge-call coin-flip
    won't trip CI but tight enough to catch real drift.

    `test_id` is normally derived from PYTEST_CURRENT_TEST; the kwarg is
    here so unit tests of this decorator can pin it deterministically.

    Anything in `**metric_kwargs` (like `pattern=` for regex_match,
    `judge=` for an LLM metric) is forwarded to the metric, filtered by
    its signature so each metric only sees the kwargs it accepts.
    """
    def decorator(test_fn: Callable) -> Callable:
        @functools.wraps(test_fn)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            result = test_fn(*args, **kwargs)

            # Tests can return either a plain string (when the metric
            # only needs the output) or an EvalOutput (when the metric
            # needs context/expected/input). Anything else is a bug in
            # user code — fail loud rather than silently mis-score.
            if isinstance(result, str):
                eval_output = EvalOutput(output=result)
            elif isinstance(result, EvalOutput):
                eval_output = result
            else:
                raise TypeError(
                    f"@eval test must return str or EvalOutput, "
                    f"got {type(result).__name__}"
                )

            score = _invoke_metric(metric, eval_output, metric_kwargs)

            metric_name = getattr(metric, "__name__", repr(metric))
            resolved_test_id = (
                test_id or _current_pytest_test_id() or "<unknown>"
            )
            # Record before the threshold check so failures still show up
            # in the results file. The user wants to see what happened on
            # a failed run, not get an empty results.json.
            runtime.record(
                test_id=resolved_test_id,
                metric=metric_name,
                score=score,
                threshold=threshold,
            )
            # Surfacing on the wrapper is convenient for users running
            # tests outside pytest (notebooks, scripts) who want the
            # score back without dipping into runtime.
            wrapper.last_score = score

            if threshold is not None and score < threshold:
                raise AssertionError(
                    f"eval threshold not met: score={score} < threshold={threshold}"
                )

            _check_regression(
                score=score,
                metric=metric,
                test_id=resolved_test_id,
                baseline_path=baseline_path,
                tolerance=regression_tolerance,
            )

            # Pytest 8+ warns on tests that return non-None. Returning
            # None keeps the wrapper compatible with both `pytest` (which
            # ignores the return) and direct calls in user code (where
            # they read `wrapper.last_score` instead).

        # Expose decorator metadata for introspection / debugging.
        wrapper._evalcheck_metric = metric
        wrapper._evalcheck_threshold = threshold
        wrapper._evalcheck_metric_kwargs = metric_kwargs
        wrapper.last_score = None
        return wrapper

    return decorator


def _invoke_metric(
    metric: Callable, eval_output: EvalOutput, metric_kwargs: dict[str, Any]
) -> float:
    """Call the metric with only the kwargs its signature accepts.

    Why not just `metric(**all_kwargs)`? Different metrics need different
    fields (faithfulness wants context, regex_match wants pattern). Filtering
    by signature lets the decorator stay generic without each metric having
    to declare a uniform interface.
    """
    sig = inspect.signature(metric)
    available = {
        "output": eval_output.output,
        "expected": eval_output.expected,
        "context": eval_output.context,
        "input": eval_output.input,
        **metric_kwargs,
    }
    relevant = {k: v for k, v in available.items() if k in sig.parameters}
    return metric(**relevant)


def _check_regression(
    score: float,
    metric: Callable,
    test_id: str,
    baseline_path: Path | str | None,
    tolerance: float,
) -> None:
    """Fail if score dropped more than `tolerance` below the committed baseline.

    Quietly returns when there's no baseline file (first run on a project)
    or no baseline entry for this test+metric (newly added test). Don't
    nag users about brand-new evals.
    """
    resolved_path = Path(baseline_path) if baseline_path else DEFAULT_BASELINE_PATH
    if not resolved_path.exists():
        return

    metric_name = getattr(metric, "__name__", repr(metric))
    baseline = load_baseline(resolved_path)
    baseline_score = baseline.get((test_id, metric_name))
    if baseline_score is None:
        return

    if score < baseline_score - tolerance:
        raise AssertionError(
            f"eval regression: score={score:.3f} < "
            f"baseline={baseline_score:.3f} (tolerance={tolerance})"
        )


def _current_pytest_test_id() -> str | None:
    """Pytest sets PYTEST_CURRENT_TEST during test execution to something
    like `tests/test_x.py::test_a (call)`. We want the part before the
    parenthetical phase indicator since that matches the IDs the GitHub
    App shows as 'Eval' in the PR comment table.
    """
    raw = os.environ.get("PYTEST_CURRENT_TEST")
    if not raw:
        return None
    return raw.split(" ")[0]
