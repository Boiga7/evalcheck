# evalcheck vs pytest-evals

Both are pytest plugins for LLM evaluation. They occupy adjacent niches and the right answer depends on how much scaffolding you want shipped versus how much you'd rather build yourself.

## Quick verdict

| You want… | Pick |
|---|---|
| The smallest possible plugin, BYO metrics | **pytest-evals** |
| Plugin that ships LLM-as-judge metrics out of the box | **evalcheck** |
| Run with custom flags (`pytest --run-eval`) | **pytest-evals** |
| Run with plain `pytest`, no flags | **evalcheck** |
| Two-phase eval/analysis (eval cases first, aggregate metrics after) | **pytest-evals** |
| Per-test threshold + git-baselined regression check | **evalcheck** |
| PR comment from a paired GitHub App | **evalcheck** |

Both are MIT, both are real pytest plugins (proper `pytest11` entry points). They overlap in the space deepeval doesn't fit cleanly into.

## Side-by-side

|  | evalcheck | pytest-evals |
|---|---|---|
| GitHub stars | (just shipped) | ~159 |
| First release | 2026 | 2024 |
| Decorator/marker style | `@eval(metric, threshold=0.7)` | `@pytest.mark.eval(name="x")` + `@pytest.mark.eval_analysis` |
| Plain `pytest` invocation | yes | needs `--run-eval` then `--run-eval-analysis` |
| Built-in metrics | 6 (faithfulness, relevance, correctness, exact_match, regex_match, custom) | 0 — bring your own |
| Two-phase architecture (case + analysis) | no — one phase per test | yes — explicit |
| LLM judge support out of the box | yes (OpenAI, Anthropic) | no — you call your own LLM in the test body |
| Regression baseline | yes — `.evalcheck/snapshots/baseline.json`, git-committed | not shipped |
| PR comment | yes (paired GitHub App) | no |
| Async test support (`pytest-asyncio`) | yes | yes |
| Parallel (`pytest-xdist`) | yes | yes |

## Worked example: the same eval in both

The task: classify customer support tickets into categories, measure accuracy across a small dataset.

### pytest-evals

```python
# test_classifier.py
import pytest

CASES = [
    {"text": "I can't log in", "expected": "auth"},
    {"text": "My card was charged twice", "expected": "billing"},
    {"text": "How do I export my data?", "expected": "support"},
]

@pytest.mark.eval(name="classifier")
@pytest.mark.parametrize("case", CASES)
def test_one(case, eval_bag, classifier):
    eval_bag.prediction = classifier(case["text"])
    eval_bag.expected = case["expected"]
    eval_bag.correct = eval_bag.prediction == eval_bag.expected

@pytest.mark.eval_analysis(name="classifier")
def test_accuracy(eval_results):
    accuracy = sum(r.correct for r in eval_results) / len(eval_results)
    assert accuracy >= 0.7
```

```bash
$ pytest --run-eval
$ pytest --run-eval-analysis
```

### evalcheck

```python
# test_classifier.py
import pytest
from evalcheck import EvalOutput, eval, exact_match

CASES = [
    {"text": "I can't log in", "expected": "auth"},
    {"text": "My card was charged twice", "expected": "billing"},
    {"text": "How do I export my data?", "expected": "support"},
]

@pytest.mark.parametrize("case", CASES)
@eval(exact_match, threshold=1.0)
def test_classifier(case, classifier):
    return EvalOutput(output=classifier(case["text"]), expected=case["expected"])
```

```bash
$ pytest
```

### What's different

pytest-evals is built around the two-phase shape: case tests collect data into `eval_bag`, then analysis tests aggregate. That's a cleaner abstraction when your "metric" is something genuinely aggregate (accuracy, F1, mean score), and you want a single pass/fail verdict for the suite.

evalcheck collapses both phases into one decorator. Each test asserts its own threshold; aggregation happens at the renderer/comment layer (in the GitHub App). Simpler if you want per-test verdicts; less expressive if you want the suite-level rollup.

## Where pytest-evals is genuinely better

- **Architectural elegance for aggregate metrics.** If "the suite passes if mean accuracy ≥ 0.7," that's `eval_analysis` exactly. evalcheck doesn't have a clean equivalent — you'd either fail individual tests at threshold=1 and look at the rollup, or compute accuracy in your own conftest.
- **Smaller and more orthogonal.** 0 built-in metrics means 0 opinions about how you score. Some teams prefer that. Especially shops with their own internal eval harness.
- **Mature.** Two years of usage feedback baked in.

## Where evalcheck is genuinely better

- **Run with `pytest`, not `pytest --run-eval --run-eval-analysis`.** Every CI config, every `.vscode/launch.json`, every Makefile that already runs `pytest` works as-is. No tooling to update.
- **Ships the metrics.** `pytest-evals` says "BYO metrics" which means "BYO LLM-as-judge prompts." Most teams write the same three or four prompts; we ship them.
- **Regression detection.** A baseline JSON in your repo, automatic comparison on every run. pytest-evals gives you the eval results — what you do with them across runs is up to you.
- **The GitHub App.** Coverage tools post PR comments, bundle-size tools post PR comments, evalcheck posts PR comments. pytest-evals doesn't currently have an analogue.

## When the answer is pytest-evals

You probably already have a homegrown LLM-as-judge function. You like the two-phase pattern. You don't want any opinionated baseline file in your repo. You want a 200-line plugin and nothing more.

## When the answer is evalcheck

You want to install one thing, decorate three tests, push, and see a PR comment 30 seconds later. You'd rather override our prompts later than write your own from scratch.

## Switching between them

Both are pytest plugins; they'll coexist in the same test directory. You could literally write some tests with `@pytest.mark.eval` and others with `@eval` and run them in the same suite. We have not tested this combination ourselves.
