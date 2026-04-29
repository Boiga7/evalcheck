"""evalcheck pytest plugin — session hooks that write results.json at session end."""

import os
from pathlib import Path

from evalcheck import runtime
from evalcheck.snapshot import save_results

DEFAULT_RESULTS_PATH = Path(".evalcheck/results.json")


def pytest_sessionstart(session):
    runtime.reset()


def pytest_sessionfinish(session, exitstatus):
    if os.environ.get("EVALCHECK_AUTOWRITE", "1") == "0":
        return
    results = runtime.collected_results()
    if not results:
        return
    save_results(DEFAULT_RESULTS_PATH, results)
