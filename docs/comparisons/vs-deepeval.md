# evalcheck vs deepeval

Both are open-source Python tools for LLM evaluation. They overlap in scope but differ sharply in shape. This page is a brutally honest comparison written by the evalcheck maintainer; cross-check anything that matters to you against deepeval's own docs.

## Quick verdict

| You want… | Pick |
|---|---|
| A polished cloud dashboard with side-by-side run comparisons | **deepeval** |
| The largest catalogue of LLM eval metrics out of the box | **deepeval** |
| Plain `pytest` invocation with no new test runner | **evalcheck** |
| Regression baselines committed to git, no SaaS account | **evalcheck** |
| A PR comment showing what regressed when CI completes | **evalcheck** (when the App ships; the plugin half is on PyPI today) |
| Existing pytest fixtures, `pytest -k`, IDE integration to keep working unchanged | **evalcheck** |

Both are MIT-licensed Python libraries. Both ship LLM-as-judge metrics. Both work in CI.

## Side-by-side

|  | evalcheck | deepeval |
|---|---|---|
| GitHub stars | (just shipped) | 15.1k |
| Test runner | plain `pytest` | `deepeval test run` (own runner) |
| Pytest plugin (entry point) | yes — `pytest11` | partial; pytest discovery yes, plain invocation no |
| `pytest -k`, `--pdb`, `pytest-xdist` work unchanged | yes | partial — depends on whether you use `deepeval test run` or `pytest` |
| Composes with existing pytest fixtures | yes — `EvalOutput` is just a return value | requires adapting to `LLMTestCase` model |
| Built-in metrics shipped | 6 (faithfulness, relevance, correctness, exact_match, regex_match, custom) | 14+ (G-Eval, faithfulness, hallucination, bias, toxicity, summarization, contextual variants…) |
| Multi-provider judge | OpenAI, Anthropic | OpenAI, Anthropic, Azure, Gemini, local |
| Regression detection | yes — git-committed JSON baseline, fails the test | yes — but compared against cloud-hosted run history |
| Cloud dashboard | no — by design | yes (Confident AI), the polished centerpiece |
| PR comment integration | yes (GitHub App, MIT) | no |
| Works in air-gapped CI | yes | partial — without Confident AI, no regression diff |
| Pricing | OSS plugin free; GitHub App free for public repos / $19/repo/mo private | OSS framework free; Confident AI cloud has paid tiers (pricing on their site) |

## Worked example: the same eval in both tools

The task: check that a one-sentence summary stays faithful to the source article.

### deepeval

```python
# test_summary.py
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

correctness = GEval(
    name="Faithfulness",
    criteria="Determine if the actual output is fully supported by the context.",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.RETRIEVAL_CONTEXT],
    threshold=0.7,
)

def test_summary():
    test_case = LLMTestCase(
        input="Summarise this:",
        actual_output=summarise(article),
        retrieval_context=[article],
    )
    assert_test(test_case, [correctness])
```

```bash
$ deepeval test run test_summary.py
```

### evalcheck

```python
# test_summary.py
from evalcheck import EvalOutput, eval, faithfulness

@eval(faithfulness, threshold=0.7)
def test_summary():
    return EvalOutput(output=summarise(article), context=article)
```

```bash
$ pytest
```

The deepeval version is ~16 lines and requires a parallel object model (`LLMTestCase`, `LLMTestCaseParams`) plus its own runner. The evalcheck version is 4 lines that look like any other pytest test, runs under plain `pytest`, and writes a results file the GitHub App reads to post a PR comment.

If you want to score along multiple dimensions deepeval doesn't ship (e.g. tone, brand voice, domain-specific rubrics), deepeval's `GEval` is more flexible — pass any criteria string and it does the rest. evalcheck has `correctness` for arbitrary rubrics but only ships one prompt template per metric; richer rubrics are a v0.2 item.

## Where deepeval is genuinely better

- **Metric catalogue.** Hallucination, bias, toxicity, summarization, contextual recall/precision — deepeval ships dedicated metrics for each. evalcheck has six and is opinionated about not adding more until they pull their weight.
- **Cloud dashboard.** Confident AI's run comparison view is polished. Drill into individual eval failures, see prompts and outputs side-by-side, share a link with a teammate. evalcheck's "dashboard" is `git log` on `.evalcheck/snapshots/baseline.json`.
- **Mindshare.** 15k+ stars means more StackOverflow answers, more tutorials, more chance that someone has already solved your edge case.

## Where evalcheck is genuinely better

- **Zero friction with existing pytest.** No new command. No new flag. No re-shaping tests around `LLMTestCase`. If you use `pytest -k`, `pytest-xdist`, `pytest-cov`, IDE pytest integration — they all keep working.
- **Vendor-free.** Your eval scores live in `git`, not someone's database. Compliance teams care about this. So do open-source maintainers.
- **PR comment is the product surface.** Coverage tools, bundle-size tools, type checkers — they show up on the PR. evalcheck makes LLM evals part of that flow.

## When the answer is "both"

You can use them together. Run deepeval's metric library inside an evalcheck `custom` callable:

```python
from evalcheck import EvalOutput, eval
from deepeval.metrics import HallucinationMetric

def hallucination_score(output: str, context: str) -> float:
    metric = HallucinationMetric(threshold=0.0)
    test_case = LLMTestCase(input="", actual_output=output, context=[context])
    metric.measure(test_case)
    return 1.0 - metric.score  # invert: 1.0 = no hallucination

@eval(hallucination_score, threshold=0.7)
def test_grounded():
    return EvalOutput(output=summarise(article), context=article)
```

You get deepeval's hallucination rubric and evalcheck's pytest-native CI integration. The cost: an extra dependency.

## What this page won't pretend

- evalcheck v0.1.0 just shipped. deepeval has years of production use across thousands of repos. Maturity matters; pick deepeval if it does.
- The GitHub App half of evalcheck — the actual PR comment — is in a separate repo (Boiga7/evalcheck-app) and not yet deployed at a public webhook URL. Plugin works today; the comment story is the next milestone.
- Many evals don't need either tool. A 30-line pytest file with a JSON dump is fine for small projects.
