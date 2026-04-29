# Contributing to evalcheck

Issues and pull requests are welcome. The plugin is small enough that a useful change is rarely more than a single file.

## Setup

```bash
git clone https://github.com/Boiga7/evalcheck.git
cd evalcheck
pip install -e ".[dev]"
pytest
```

You should see the full test suite pass on Python 3.10–3.13. If anything's red on a fresh clone, open an issue — that's a bug, not a "your environment" problem.

## Running the suite

```bash
pytest                              # full run
pytest tests/test_metrics.py -v     # one file
coverage run -m pytest && coverage report
```

CI gates on coverage at 95%. Tests cover the decorator, the snapshot format, the judge providers (with respx mocks — no real LLM calls in CI), and the pytest plugin hooks.

## What makes a good PR

- **Bug fixes** — include a failing test in the same PR. The TDD discipline is what keeps the plugin from accidentally breaking pytest's contract over time.
- **New metrics** — they live in `evalcheck/metrics/`. A metric is any callable returning a float in `[0, 1]`. If yours is judge-based, see `judge_metrics.py` for the prompt-template pattern.
- **New providers** — they live in `evalcheck/judge.py`. Implement the `Judge` protocol (`score(system, user) -> JudgeResponse`). Test with `respx` mocks the way `OllamaJudge` and `OpenAIJudge` do.

## What's out of scope

The README has a section called "What it doesn't do". A non-exhaustive list of things we'll politely decline:

- Hosted dashboards, web playgrounds, GUIs — keep the plugin file-based.
- Slack/Teams/Discord notifications — handled at the GitHub App layer or by other tools.
- Replacing pytest as the test runner — the whole point is staying compatible.

If your idea overlaps any of those, open an issue first to discuss before opening a PR.

## Style

- Type hints everywhere. The plugin is type-checked in CI via `mypy --strict` (TBD; currently best-effort).
- Comments explain the *why* and the gotchas, not the *what*. Code already says what.
- One assertion per test where reasonable — failures should pinpoint the broken behaviour.

## Licence

By contributing, you agree your contributions are licensed under the [MIT licence](LICENSE) on the same terms as the rest of the project.
