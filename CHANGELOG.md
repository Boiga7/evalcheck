# Changelog

All notable changes to evalcheck.

## [0.2.0] - 2026-04-29

### Added
- `OllamaJudge` — local-first judge backed by Ollama's OpenAI-compatible endpoint at `http://localhost:11434/v1`. Configurable via `EVALCHECK_JUDGE_MODEL=ollama:llama3.2:3b` or `EVALCHECK_OLLAMA_HOST` for remote instances.
- `make_judge` factory now accepts `ollama:<model>` specs.

### Changed
- Plain-language code comments throughout the source explaining the why and the gotchas the project has hit (PEM normalisation, PKCS#1 vs PKCS#8, workflow_run.pull_requests reliability, etc).

### Fixed
- None — 0.1.0 was found to work correctly end-to-end on 2026-04-29 after fixing the matching issues in the GitHub App (separate repo).

## [0.1.0] - 2026-04-29

First public release of the OSS pytest plugin.

### Added
- `@eval` decorator that wraps a pytest test, runs a metric on its return value, and asserts a threshold.
- `EvalOutput` dataclass for tests that need to pass `context`, `expected`, `input`, or `metadata` to the metric.
- Deterministic metrics: `exact_match`, `regex_match`.
- LLM-as-judge metrics: `faithfulness`, `relevance`, `correctness`.
- Multi-provider judge runner (`OpenAIJudge`, `AnthropicJudge`, `make_judge` factory). Configurable via `EVALCHECK_JUDGE_MODEL`.
- Snapshot-based regression detection: results compared against `.evalcheck/snapshots/baseline.json` on every run; fails if score drops below `baseline - regression_tolerance`.
- pytest plugin hooks (`pytest_sessionstart`, `pytest_sessionfinish`) that auto-write `.evalcheck/results.json` after every run.
- `evalcheck snapshot --update` CLI to bless `results.json` as the new baseline.
- Plain `pytest` invocation. No new test runner, no special flags.

### Notes
- 100% test coverage (65 tests).
- The GitHub App that consumes `results.json` and posts the PR comment is the next milestone — not part of this release.
