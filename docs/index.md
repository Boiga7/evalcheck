# evalcheck docs

## Comparisons

How evalcheck stacks up against the alternatives — written by the maintainer, opinionated where it matters, honest where the other tool is genuinely better.

- [evalcheck vs deepeval](comparisons/vs-deepeval.md) — the largest LLM eval framework in Python today
- [evalcheck vs pytest-evals](comparisons/vs-pytest-evals.md) — the closest pytest-native analogue

Coming next:

- evalcheck vs promptfoo (JS-first, YAML config)
- evalcheck vs braintrust (hosted, premium)
- evalcheck vs Inspect (research-shaped, UK AISI)

## Schema reference

The `llms.txt` at the repo root is the canonical machine-readable summary of the API surface — meant for AI agents (Claude Code, Cursor, GPT) consuming the docs programmatically.

## Repository layout

```
evalcheck/                  # pytest plugin (this repo)
├── evalcheck/              # source
├── tests/                  # 69 tests, 100% coverage
├── docs/                   # this directory
├── examples/               # runnable notebooks (LangChain, LlamaIndex, OpenAI)
├── README.md               # product overview
├── CHANGELOG.md            # release history
├── CONTRIBUTING.md
├── PRIVACY.md / TERMS.md / SECURITY.md
└── LICENSE                 # MIT

evalcheck-app/              # GitHub App (separate repo)
├── src/                    # diff + render + GitHub API helpers
├── api/webhook.ts          # Vercel function entry
├── DEPLOY.md               # 15-minute self-host walkthrough
└── README.md
```
