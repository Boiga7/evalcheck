# LLM Eval Tooling — Landscape Scan

Date: 2026-04-29
Purpose: validate the wedge for a pytest-shaped LLM eval product before writing any code.

## Competitors

| Tool | Stars | Runner | Pytest-native? | Metrics shipped | Regression tracking | Pricing |
|---|---|---|---|---|---|---|
| **deepeval** | 15.1k | own (`deepeval test run`) | partial — pytest discovery, NOT plain `pytest` | yes (GEval, faithfulness, bias, etc.) | cloud-tied (Confident AI) | "free" cloud, paid tiers undisclosed |
| **pytest-evals** (AlmogBaku) | 159 | pytest with `--run-eval` flag | yes — real plugin via marks | no — BYO metrics | local JSON between phases, no baseline | OSS, no hosted offering |
| **promptfoo** | 20.7k | own CLI, YAML config | no | yes | feedback loop, no commit tracking detailed | undisclosed |
| **braintrust** | n/a | SDK + hosted | no | yes | hosted, commit-linked | $0 starter / $249/mo Pro |
| **inspect-ai** | n/a | own (`inspect eval`) | no | yes (Tasks/Solvers/Scorers) | none built-in | OSS only |
| **ragas** | n/a | library called from Python | neutral | yes (RAG metrics, custom decorators) | none built-in | OSS + paid consulting |
| **langfuse** | n/a | observability SDK | no | yes (eval as one feature) | hosted | OSS self-host + paid cloud |

## What each tool gets right

- **deepeval** — best-in-class metric library + cloud regression dashboard. Owns the "LLM eval framework for Python" mindshare.
- **pytest-evals** — proves the "real pytest plugin" pattern works (marks + fixtures + xdist + asyncio compose cleanly).
- **promptfoo** — wins on JS/TS + YAML simplicity + 20k stars of inertia.
- **braintrust** — wins on hosted polish for teams with budget.
- **inspect-ai** — wins on safety/research depth.

## What's missing across all of them

1. **Run with plain `pytest` — no new command, no special flag.** deepeval requires `deepeval test run`. pytest-evals requires `--run-eval` / `--run-eval-analysis`. Every existing pytest CI config, IDE runner integration, coverage tool, and `pytest -k`/`-n auto` muscle memory breaks.
2. **Git-committed regression baselines.** All regression tracking lives in someone's cloud (Confident AI, Braintrust, Langfuse). Air-gapped CI, OSS contributors, and "I don't want vendor lock-in" teams have no clean option.
3. **PR-comment-shaped output.** No tool I scanned produces a markdown PR comment showing which evals regressed/improved vs. the base branch. This is the standard pattern for coverage tools, bundle-size tools, visual diff tools — but absent for LLM evals.
4. **Composes with existing pytest fixtures cleanly.** deepeval's `LLMTestCase` is a parallel object model; you can't reuse your `client`, `db`, `mock_llm` fixtures without adapter glue.

## The honest wedge assessment

The original pitch — "pytest plugin for LLM evals" — is partially occupied:
- deepeval owns the metrics + cloud combination.
- pytest-evals owns the "barebones pytest-native" combination.

Three remaining wedges in descending honesty:

### Wedge A — "deepeval's metrics, pytest-evals' pytestness, no cloud lock-in"
A real gap, but narrow. Risk: pytest-evals could add metrics in one weekend; deepeval could add a true plugin. Defensibility is thin. 159 stars on pytest-evals after 10 months also suggests the "pure pytest, BYO metrics" angle has weak pull.

### Wedge B — "Eval-as-PR-comment GitHub App"
A real gap, non-overlapping with all 7 competitors. The product surface is the GitHub PR comment ("Faithfulness regressed 0.84 → 0.71 on `test_summarization`"); the underlying engine is still a pytest plugin. Distribution loop is GitHub Marketplace, which compounds. Founder's CI + Playwright + AI-workflow background maps directly.

### Wedge C — "Eval CI for AI-assisted-development loops"
Specifically: testing agent loops (tool-calling, Claude Code-style coding agents), not just prompt outputs. Adjacent to mcpguard and possibly mergeable with it. Less crowded but smaller buyer pool today.

## Recommendation

Ship **Wedge B** if we ship anything in this space. The PR-comment surface is what makes this a product instead of a library, and it's the only positioning that doesn't require knife-fighting deepeval.

If Wedge B doesn't feel right, the honest call is to walk away from this category and put the weekends into mcpguard, where the QA × LLM unfair advantage is sharper and the field is genuinely empty.

## Decision needed before writing README

- (a) Pivot to Wedge B (PR-comment GitHub App, pytest plugin underneath).
- (b) Push on Wedge A anyway — accept the narrow defensibility because it's faster to ship.
- (c) Kill evalpytest, pivot the weekends to mcpguard.
