# evalcheck docs

## Comparisons

How evalcheck stacks up against the alternatives — written by the maintainer, opinionated where it matters, honest where the other tool is genuinely better.

- [evalcheck vs deepeval](comparisons/vs-deepeval.md) — the largest LLM eval framework in Python today
- [evalcheck vs pytest-evals](comparisons/vs-pytest-evals.md) — the closest pytest-native analogue

Coming next:

- evalcheck vs promptfoo (JS-first, YAML config)
- evalcheck vs braintrust (hosted, premium)
- evalcheck vs Inspect (research-shaped, UK AISI)

## Outreach drafts

Pre-flight notes for contributing examples upstream and submitting a Show HN. These live in [`outreach/`](../outreach/) and explain *why* each PR is shaped the way it is — not just the copy itself.

## Schema reference

The `llms.txt` at the repo root is the canonical machine-readable summary of the API surface — meant for AI agents (Claude Code, Cursor, GPT) consuming the docs programmatically.

## Repository layout

```
evalcheck/                  # pytest plugin (this repo)
├── evalcheck/              # source
├── tests/                  # 65 tests, 100% coverage
├── docs/                   # this directory
├── outreach/               # Show HN, cookbook PR drafts
├── README.md               # product overview
├── LANDSCAPE.md            # competitive scan that produced the wedge
├── v1-plugin-plan.md       # build plan (DONE)
└── SHIPPING.md             # PyPI release walkthrough

evalcheck-app/              # GitHub App (separate repo)
├── src/                    # diff + render + GitHub API helpers
├── api/webhook.ts          # Vercel function entry
├── DEPLOY.md               # 15-minute deployment walkthrough
└── ...
```
