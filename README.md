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
from evalcheck import EvalOutput, eval, faithfulness

@eval(faithfulness, threshold=0.75)
def test_summary():
    article = load_fixture("article.md")
    summary = summarise(article)
    return EvalOutput(output=summary, context=article)
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

The pytest-native path matters because eval logic shares fixtures with the rest of your test suite: the same DB seeded the same way, the same mocked HTTP client, the same auth context. Running evals as a parallel test framework doubles the surface area and rots within a quarter.

## Built-in metrics

- `faithfulness` — output grounded in the supplied context (LLM-as-judge)
- `relevance` — output answers the input (LLM-as-judge)
- `correctness` — output matches the expected answer, allowing paraphrase (LLM-as-judge)
- `exact_match` — deterministic string equality
- `regex_match` — deterministic pattern match
- `custom(fn)` — any callable returning a float in [0, 1]

Multi-provider judge: OpenAI, Anthropic, and Ollama (local) out of the box. Configurable per metric or globally via `EVALCHECK_JUDGE_MODEL`.

## Examples

Runnable Jupyter notebooks under [`examples/`](examples/) for the most common stacks:

- [`langchain_rag.ipynb`](examples/langchain_rag.ipynb) — LangChain RAG pipeline → faithfulness + correctness in CI
- [`llamaindex_query_engine.ipynb`](examples/llamaindex_query_engine.ipynb) — LlamaIndex `QueryEngine` → faithfulness + relevance
- [`openai_judge_in_ci.ipynb`](examples/openai_judge_in_ci.ipynb) — OpenAI `response_format: json_object` for a homegrown judge metric

## Comparisons

Honest comparisons against the alternatives, written by the maintainer:

- [evalcheck vs deepeval](docs/comparisons/vs-deepeval.md) — the largest LLM eval framework in Python
- [evalcheck vs pytest-evals](docs/comparisons/vs-pytest-evals.md) — the closest pytest-native analogue

## Pricing

- **OSS plugin** (`pip install evalcheck`) — MIT, free forever. Runs locally and in CI. Writes baselines to `.evalcheck/snapshots/`. Full functionality without ever signing up.
- **Free** GitHub App tier — public repos and the first 50 evals per private-repo run. Includes the PR comment, the GitHub Check status, and the diff against your baseline.
- **Pro** — $19 per private repo per month, billed via [GitHub Marketplace](https://github.com/marketplace/evalcheck). Unlimited evals per run, priority support, and the hosted dashboard tier when it ships.

The OSS plugin is intentionally complete on its own. The Pro tier exists for teams that have outgrown the free quota; teams that prefer their own CI tooling can render the JSON output however they want.

## What it doesn't do

- Host your eval history (it's git-committed).
- Generate datasets for you.
- Track cost or latency (use observability tools).
- Slack, Teams, or Discord integrations (the PR comment is the surface).
- SSO, RBAC, multi-repo org views.
- A web playground.

Keeping the surface this small is what lets one person maintain it. Adjacent features earn their place by being requested by paying users, not by guesswork.

## Configuration

The decorator is the configuration surface. There is no global `[tool.evalcheck]` config in v0.2; per-decorator overrides cover everything users have asked for so far.

```python
@eval(
    metric,                       # any callable returning a float in [0, 1]
    threshold=0.7,                # fail if score below this
    regression_tolerance=0.05,    # fail if score drops > this below baseline
    baseline_path=None,           # default: .evalcheck/snapshots/baseline.json
    judge=None,                   # custom judge for LLM-as-judge metrics
)
```

Provider env vars:

- `EVALCHECK_JUDGE_MODEL` — e.g. `openai:gpt-4o-mini`, `anthropic:claude-haiku-4-5`, `ollama:llama3.2:3b`
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` — passed through to the respective SDKs
- `EVALCHECK_OLLAMA_HOST` — for remote Ollama servers (defaults to `http://localhost:11434`)

## CLI

```bash
evalcheck snapshot --update     # bless results.json as the new baseline
```

## Adding the GitHub App

1. Install [evalcheck](https://github.com/marketplace/evalcheck) from the GitHub Marketplace.
2. Pick the repos you want it to watch.
3. Add an `actions/upload-artifact@v4` step to your CI workflow that uploads `.evalcheck/results.json` under the name `evalcheck-results`.
4. Push a PR. The comment shows up automatically.

A full setup walkthrough lives in the [evalcheck-app repo](https://github.com/Boiga7/evalcheck-app).

## Contributing

Issues and PRs welcome. The plugin is small enough that a useful change is rarely more than a single file. Run the test suite with `pytest`; coverage is enforced at 95% in CI.

## License

MIT.
