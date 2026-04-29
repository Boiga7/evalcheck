# evalcheck

[![PyPI](https://img.shields.io/pypi/v/evalcheck)](https://pypi.org/project/evalcheck/)
[![Python](https://img.shields.io/pypi/pyversions/evalcheck)](https://pypi.org/project/evalcheck/)
[![License](https://img.shields.io/pypi/l/evalcheck)](LICENSE)
[![CI](https://github.com/Boiga7/evalcheck/actions/workflows/ci.yml/badge.svg)](https://github.com/Boiga7/evalcheck/actions/workflows/ci.yml)
[![Downloads](https://img.shields.io/pypi/dm/evalcheck)](https://pypi.org/project/evalcheck/)

> Bundlesize for your LLM evals. A pytest plugin and GitHub App that posts a PR comment showing which evals regressed, improved, or are new — every time you push.

## The pitch

You change a prompt, swap a model, or tweak a RAG pipeline. Did quality go up or down? Today the answer is "run the evals locally, eyeball the numbers, hope you remembered to commit them."

evalcheck makes the answer a PR comment.

```
## evalcheck — 24 evals run on commit a1b2c3d

| Eval | main | this PR |   Δ    |
|------|------|---------|--------|
| test_summarization::faithfulness | 0.84 | 0.71 | -0.13 |
| test_qa::relevance               | 0.91 | 0.93 | +0.02 |
| test_classifier::accuracy        | 0.87 | 0.87 |   —   |

1 regression, 1 improvement, 22 unchanged.
GitHub Check: failing — faithfulness dropped below 0.75 threshold.
```

That comment, on every push, is the entire product.

## Install

```bash
pip install evalcheck
```

```python
# tests/test_summarization.py
from evalcheck import eval, faithfulness

@eval(metric=faithfulness, threshold=0.75)
def test_summary(article):
    return summarize(article)
```

```bash
pytest
```

Plain `pytest`. No new runner, no flags, no cloud account. The first run writes a baseline to `.evalcheck/snapshots/`. Commit it. Subsequent runs diff against it.

Add the GitHub App, push the branch, and the PR comment shows up.

## How it differs

|  | evalcheck | deepeval | pytest-evals | promptfoo | braintrust |
|---|---|---|---|---|---|
| Plain `pytest` invocation | yes | needs `deepeval test run` | needs `--run-eval` flag | own CLI | SDK-only |
| Ships LLM-as-judge metrics | yes | yes | bring your own | yes | yes |
| Regression baseline in git, not cloud | yes | cloud-tied | none | none | cloud |
| PR comment per push | yes | no | no | no | no |
| GitHub Check API status | yes | no | no | no | no |
| Composes with existing pytest fixtures | yes | adapter required | yes | n/a | n/a |

The wedge is the bottom three rows. Nobody else ships them.

## Why this exists

Every meaningful CI signal in modern dev — coverage, bundle size, type errors, accessibility — shows up as a PR comment or a Check status. Engineers triage from the PR view, not from a separate dashboard. LLM eval tooling skipped that pattern. evalcheck closes the gap.

The pytest-native path matters because eval logic shares fixtures with the rest of your test suite: the same DB seeded the same way, the same mocked HTTP client, the same auth context. Running evals as a separate parallel test framework doubles the surface area and rots within a quarter.

## Pricing

- **OSS plugin** (`pip install evalcheck`) — MIT, free forever. Runs locally and in CI. Writes baselines to `.evalcheck/snapshots/`. Full functionality without ever signing up.
- **GitHub App** — free for public repos and the first 50 evals per private-repo run. $19 per private repo per month above that.
- **Hosted dashboard** (later, optional) — historical trend lines, model-vs-model side-by-sides, drill-into-failures. $49/team/month. Reads the same JSON snapshots — opting in changes nothing about how the plugin runs.

The OSS plugin is intentionally complete on its own. The GitHub App and dashboard are pure convenience layers; teams that prefer their own CI tooling can render the JSON output however they want.

## Built-in metrics (v1)

- `faithfulness` — output grounded in the supplied context (LLM-as-judge)
- `relevance` — output answers the input
- `correctness` — output matches an expected answer (LLM-as-judge with a rubric)
- `exact_match` — deterministic string equality
- `regex_match` — deterministic pattern match
- `custom(fn)` — arbitrary scorer returning a float in [0, 1]

Multi-provider out of the box (OpenAI, Anthropic, local via Ollama). Judge model configurable per metric.

## Roadmap

| Weeks | Phase | Output |
|---|---|---|
| 1–3 | Plugin v1 | `pip install evalcheck` works. `@eval` decorator, 6 built-in metrics, JSON snapshot, plain `pytest` invocation, multi-provider. OSS on GitHub from day one. llms.txt on docs. |
| 4–6 | GitHub App v1 | Webhook receives push, runs evals in a sandboxed runner, posts PR comment, sets Check status. Free tier live. |
| 7–9 | First 10 paying installs | Cookbook PRs into LangChain, LlamaIndex, OpenAI examples. One honest "Show HN" post. Direct outreach to maintainers of public AI repos that already have eval scripts in the repo but no CI integration. No sales calls. |
| 10–12 | Compounding distribution | Programmatic SEO: `evalcheck vs deepeval`, `evalcheck vs pytest-evals`, `LLM eval CI GitHub Action`. Marketplace listing. Badge embed on README. PyPI download counter on landing page. |

## What's not in v1

- Hosted historical dashboard — use `git log` on `.evalcheck/snapshots/`
- Automatic dataset generation
- Slack / Teams / Discord notifications
- SSO, RBAC, multi-repo org views
- Cost / latency tracking (it's a separate concern; observability tools own that)
- A web playground

Keeping the surface this small is the only way one person ships a working product in 12 weekends.

## Kill criterion

Day 90: under 500 weekly PyPI downloads **and** under 3 paying GitHub App installs. Either alone is salvageable; both together means the bundlesize-for-prompts framing didn't land and the OSS-to-paid funnel isn't compounding. Walk away cleanly — keep the OSS plugin published, take the lessons into mcpguard.

## Honest risks

- **deepeval can ship a real pytest plugin in a weekend.** They have 15.1k stars of momentum. Mitigation: get the GitHub App and PR-comment surface live fast — that's the moat, not the plugin.
- **`pytest-evals` can ship metrics in a weekend.** They have the pytest-native pattern down. Mitigation: same — the comment surface and GitHub Check are non-trivial to add and require infra they don't have.
- **The "engineers will adopt LLM evals in CI" bet.** Not yet a default behaviour for most teams. evalcheck has to teach the habit while selling the tool. Distribution is the harder half of the work.

## Status

Pre-build. README written first deliberately — if the pitch isn't compelling on this page, no amount of code rescues it. If you read this far and the wedge feels real, that's the green light.
