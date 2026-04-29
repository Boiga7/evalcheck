# dev.to launch article — paste-ready

Submit at https://dev.to/new (any account works; no karma gate).

Tags to add (dev.to allows up to 4): `python`, `pytest`, `llm`, `ci`

Cover image: skip; their default works fine for technical posts.

---

## Title

> The CI signal LLM dev tooling is missing: a PR comment

## Body

Every meaningful CI signal in modern dev shows up as a PR comment. Coverage tools post a comment. Bundle-size tools post a comment. Type checkers, linters, accessibility scanners — all of them post on the PR so engineers can triage from one screen without bouncing to a separate dashboard.

LLM eval tooling skipped that pattern.

Today, when you change a prompt or swap a model, the question "did quality go up or down" gets answered one of three ways:

1. Run the evals locally, eyeball the numbers, hope you remember to commit them.
2. Pay for a SaaS that holds your eval history (and your budget approval forever).
3. Don't run evals in CI at all because the tooling is too heavy to maintain.

I shipped a small tool last week that closes that gap. It's called [evalcheck](https://github.com/Boiga7/evalcheck), it's a pytest plugin and a paired GitHub App, and the entire product surface is the comment that shows up on your PR every time CI completes.

```
## evalcheck — 24 evals run on commit a1b2c3d

| Eval | base | this PR |   Δ    |
|------|------|---------|--------|
| test_summarization::faithfulness | 0.84 | 0.71 | -0.13 |
| test_qa::relevance               | 0.91 | 0.93 | +0.02 |
| test_classifier::accuracy        | 0.87 | 0.87 |   —   |

1 regression, 1 improvement, 22 unchanged.
```

That comment, on every push, is the entire product.

## How it actually works

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

That's it. Plain `pytest`. No new test runner, no `--run-eval` flag, no cloud signup. The plugin writes a `results.json` after the run; the first run becomes your baseline (`evalcheck snapshot --update` blesses it); subsequent runs fail when scores drop more than a tolerance below baseline.

The baseline lives in `git`. It's a JSON file in your repo, committable, reviewable, diffable. No SaaS holds your eval history. If evalcheck disappears tomorrow, your evals don't.

## Six built-in metrics

Three LLM-as-judge:

- `faithfulness` — is the output grounded in the supplied context (RAG / summarisation)
- `relevance` — does the output answer the input
- `correctness` — does the output match the expected answer (semantic, allows paraphrase)

Three deterministic:

- `exact_match` — string equality
- `regex_match` — pattern match
- `custom(fn)` — any callable returning a float in [0, 1]

Judge metrics work with OpenAI, Anthropic, and Ollama (local models). Configurable via one env var.

## Why pytest-native specifically

LLM eval tools fall into two camps:

- **Frameworks with their own runner** — deepeval (`deepeval test run`), pytest-evals (`--run-eval`), promptfoo (own CLI). They each break plain `pytest`. Existing CI configs need updating, IDE pytest integration breaks, `pytest -k` muscle memory dies.
- **Cloud-first** — braintrust, langfuse. Your data lives in their database. Air-gapped CI is out.

evalcheck is the third option. It's a real `pytest11` plugin (entry point in pyproject.toml, discoverable by pytest, composes with existing fixtures), and the baseline is a file in `git`. Nothing extra to install in CI. Nothing locked to a vendor.

The pytest-native bit matters more than it sounds. Eval logic shares fixtures with the rest of your test suite — same DB seeded the same way, same mocked HTTP client, same auth context. Running evals as a parallel test framework doubles the surface area and rots within a quarter.

## What it's not

I deliberately stopped at six metrics. There's no hosted dashboard. No automatic dataset generation. No Slack integration. No web playground. The list of "what's not in v1" in the README is longer than the list of what is.

This isn't deepeval. deepeval has 14+ metrics and a polished cloud dashboard. If you want metric breadth and a UI, use deepeval — they've earned 15k stars on a real product.

evalcheck is for teams who:

- Already use pytest and don't want a parallel test framework.
- Want their eval baseline in git, not a SaaS.
- Want a PR comment on every push without writing the comment-rendering code themselves.

## Honest about the state

Plugin is on PyPI today (v0.2.0, MIT). The GitHub App is deployed and posting comments end-to-end on the project's own repo. Real-world battle-testing on outside repos is the next milestone — that's where the gnarly artifact-layout edge cases live.

Source: https://github.com/Boiga7/evalcheck
PyPI: https://pypi.org/project/evalcheck/
Comparisons against deepeval / pytest-evals: in the repo at `docs/comparisons/`

If you try it, the part I'm least confident in is the LLM-as-judge prompt templates. They're short by design (long judge prompts make scores noisier in my experience), but I'd love feedback from anyone who's tuned judge prompts seriously.
