"""The @eval decorator — runs a metric against a test's return value."""

import functools
import inspect
import os
from pathlib import Path
from typing import Any, Callable

from evalcheck import runtime
from evalcheck.snapshot import load_baseline
from evalcheck.types import EvalOutput

DEFAULT_BASELINE_PATH = Path(".evalcheck/snapshots/baseline.json")


def eval(
    metric: Callable[..., float],
    threshold: float | None = None,
    regression_tolerance: float = 0.05,
    baseline_path: Path | str | None = None,
    test_id: str | None = None,
    **metric_kwargs: Any,
) -> Callable:
    def decorator(test_fn: Callable) -> Callable:
        @functools.wraps(test_fn)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            result = test_fn(*args, **kwargs)

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
            runtime.record(
                test_id=resolved_test_id,
                metric=metric_name,
                score=score,
                threshold=threshold,
            )
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

        wrapper._evalcheck_metric = metric
        wrapper._evalcheck_threshold = threshold
        wrapper._evalcheck_metric_kwargs = metric_kwargs
        wrapper.last_score = None
        return wrapper

    return decorator


def _invoke_metric(
    metric: Callable, eval_output: EvalOutput, metric_kwargs: dict[str, Any]
) -> float:
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
    raw = os.environ.get("PYTEST_CURRENT_TEST")
    if not raw:
        return None
    return raw.split(" ")[0]
