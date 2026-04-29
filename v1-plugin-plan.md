# evalcheck v1 — plugin implementation plan

Status: **DONE** (2026-04-29). Version 0.1.0 in `pyproject.toml`, 61 tests passing, 97% coverage. Ready for PyPI release pending git/GitHub setup.

Scope: just the OSS pytest plugin (weekends 1-3 in the README roadmap). The GitHub App is a separate plan; this one stops at "JSON results emitted to disk."

## API the user sees

```python
from evalcheck import eval, faithfulness, EvalOutput

@eval(metric=faithfulness, threshold=0.75)
def test_summary():
    article = load_fixture("article.md")
    summary = summarize(article)
    return EvalOutput(output=summary, context=article)
```

- Decorator wraps a normal pytest function.
- Test function returns either a `str` (output only) or `EvalOutput(output, context=None, expected=None, metadata=None)`.
- Plugin scores the return, compares to baseline, fails the test if below threshold OR if score regressed by more than `regression_tolerance` (default 0.05) vs baseline.

Plain `pytest` runs everything. Plain pytest fixtures compose. `pytest -k`, `pytest -n auto`, `pytest --pdb` all work.

## Package layout

```
evalcheck/
  __init__.py          # public API: eval, EvalOutput, faithfulness, ...
  plugin.py            # pytest hookimpls (pytest_collection_modifyitems, pytest_runtest_makereport)
  decorator.py         # @eval implementation; stores metric+threshold on the test item
  metrics/
    __init__.py
    faithfulness.py    # LLM-as-judge: is output grounded in context?
    relevance.py       # LLM-as-judge: does output answer the input?
    correctness.py     # LLM-as-judge: matches expected per rubric
    deterministic.py   # exact_match, regex_match
    custom.py          # custom(fn) wrapper
  judge.py             # provider-agnostic LLM call (OpenAI, Anthropic in v1)
  snapshot.py          # read/write .evalcheck/snapshots/
  report.py            # JSON output for the GitHub App
  config.py            # pyproject.toml [tool.evalcheck] parsing
tests/
  test_decorator.py
  test_metrics.py
  test_snapshot.py
  test_plugin_integration.py   # uses pytester
pyproject.toml
README.md              # adapted from the product README
LICENSE                # MIT
```

## Order of work

### Weekend 1 — minimum viable decorator
1. `pyproject.toml` with `pytest11` entry point.
2. `EvalOutput` dataclass, `@eval` decorator that just records `(metric, threshold)` on the function.
3. `pytest_runtest_makereport` hook that, on test pass, invokes the metric on the return value and asserts threshold.
4. Two deterministic metrics: `exact_match`, `regex_match`. No LLM calls yet.
5. End of weekend 1: `pip install -e .` + a `test_demo.py` with `@eval(metric=exact_match, threshold=1.0)` runs under plain `pytest` and fails when the output doesn't match.

### Weekend 2 — LLM-as-judge metrics + snapshots
1. `judge.py`: provider abstraction with OpenAI + Anthropic adapters. Configurable judge model via env var. Prompt templates per metric stored in `metrics/prompts/`.
2. `faithfulness`, `relevance`, `correctness` implemented as judge calls returning a float [0,1].
3. `snapshot.py`: read `.evalcheck/snapshots/baseline.json`, fall back gracefully if missing.
4. Threshold logic: fail if `score < threshold` OR if `score < baseline_score - regression_tolerance`.
5. End of weekend 2: a real LLM eval test passes/fails based on a judge call and a baseline diff.

### Weekend 3 — config, multi-provider, report output
1. `[tool.evalcheck]` config in `pyproject.toml` (judge model, regression_tolerance, snapshot dir).
2. `report.py` emits `.evalcheck/results.json` after the run for the GitHub App to consume.
3. `evalcheck` CLI with one command: `evalcheck snapshot --update` to bless current results as the new baseline.
4. Own pytest suite: 80%+ coverage on `decorator.py`, `snapshot.py`, `metrics/deterministic.py`. Mock the judge for `metrics/*` tests.
5. README polish, PyPI release as `0.1.0`.

## Decisions made

- **No litellm dependency.** Direct `openai` + `anthropic` SDKs. Cuts dependency weight significantly. Adding Ollama/Bedrock/Gemini happens via the same `Provider` interface in v1.1.
- **Snapshots are git-committed.** `.evalcheck/snapshots/baseline.json` lives in the repo. No cloud, no signup, works in air-gapped CI. The GitHub App will diff `baseline.json` between commits.
- **One snapshot file per repo, not per test.** Easier to diff in PR review, fewer files to track. Format: `{schema_version: 1, runs: [{test_id, metric, score, threshold, timestamp, ...}]}`.
- **No retry / no caching of judge calls in v1.** Determinism is faked via `temperature=0` on the judge model. If users need retries, they wrap externally.
- **Async tests work via pytest-asyncio.** We don't ship our own runner. If pytest-asyncio is installed, `@eval` on an async test just works.
- **Threshold semantics.** Two failure modes: hard threshold (`score < 0.7`) and regression (`score < baseline - 0.05`). Both controlled via decorator args, regression_tolerance configurable globally.

## Open questions for the founder before weekend 1 starts

None blocking. v1 ships against this spec as written. If anything changes mid-build, it'll be reported as a deviation, not pre-asked.

## Definition of done for v1

- `pip install evalcheck` works on Python 3.10+.
- Six built-in metrics (3 judge-based, 2 deterministic, 1 custom).
- Plain `pytest` invocation runs evals; no flags required.
- JSON snapshot baseline + JSON results output.
- 80%+ test coverage on the plugin's own suite.
- README on PyPI matches the product README.
- v0.1.0 published to PyPI.

## What v1 explicitly does NOT include

- The GitHub App (next plan).
- The hosted dashboard (later, optional).
- Any provider beyond OpenAI and Anthropic.
- Cost tracking, latency metrics, traces.
- A web UI of any kind.
- Slack/Teams/Discord integrations.
- Datasets, parametrize helpers (use `pytest.mark.parametrize` directly).

If a user asks for any of the above in week 1, the answer is "v2." Hard scope discipline is the only way 12 weekends of solo work produces a real product instead of a half-done framework.
