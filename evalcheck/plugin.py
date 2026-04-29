"""Pytest plugin entry point — session-level hooks.

Registered via the `pytest11` entry point in pyproject.toml so pytest
discovers it automatically when this package is installed. There's no
config we need from pytest itself; everything's driven by the @eval
decorator at call time.
"""

import os
from pathlib import Path

from evalcheck import runtime
from evalcheck.snapshot import save_results

# Where the GitHub App expects to find the results file. Hardcoded
# rather than configurable for v0.1 — one less knob for users to get
# wrong. Override is possible by setting EVALCHECK_AUTOWRITE=0 and
# writing the file yourself in conftest.
DEFAULT_RESULTS_PATH = Path(".evalcheck/results.json")


def pytest_sessionstart(session):
    """Wipe the runtime accumulator at the start of each session.

    Important when pytest is invoked programmatically (pytester self-tests,
    embedded test runners). Without this, results from a previous in-process
    session would leak into the new one.
    """
    runtime.reset()


def pytest_sessionfinish(session, exitstatus):
    """Write `.evalcheck/results.json` if anything was recorded.

    Skipped when EVALCHECK_AUTOWRITE=0 — used by our own test suite to
    avoid clobbering the dev folder with a results file every time we
    run pytest on the plugin itself. Real users get auto-write by default.
    """
    if os.environ.get("EVALCHECK_AUTOWRITE", "1") == "0":
        return
    results = runtime.collected_results()
    # No results means no @eval-decorated tests ran. Don't create an
    # empty file — confusing and pollutes git status.
    if not results:
        return
    save_results(DEFAULT_RESULTS_PATH, results)
