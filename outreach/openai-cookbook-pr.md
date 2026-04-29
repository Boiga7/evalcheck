# OpenAI Cookbook PR draft

**Target repo:** https://github.com/openai/openai-cookbook
**Approach:** highest-traffic of the three. Standards are tighter — bias toward demonstrating an OpenAI feature, not your tool. Frame it as "how to use OpenAI for LLM eval CI" with evalcheck as the supporting infrastructure.

---

## Pre-flight

1. Read https://github.com/openai/openai-cookbook/blob/main/CONTRIBUTING.md carefully — they explicitly require notebooks, not markdown.
2. Their bar: "demonstrably useful pattern that uses the OpenAI API." Don't lead with the third-party tool.
3. They moderate heavily. Expect 1–4 weeks before maintainer feedback.
4. Submit fewer, better PRs here than to LlamaIndex/LangChain. Quality over volume.

## Notebook title

`Regression-testing LLM-as-judge evals in CI with OpenAI`

## Notebook intro (markdown cell)

> When you change a prompt or swap a model, you want fast feedback on whether quality went up or down. This notebook shows a simple, CI-friendly pattern:
>
> 1. Use OpenAI's `chat.completions` with `response_format: json_object` to score outputs against a rubric.
> 2. Capture those scores in a snapshot file committed to your repo.
> 3. Fail CI if scores drop below a tolerance.
>
> The pattern works with any pytest-shaped runner. This notebook uses [evalcheck](https://github.com/Boiga7/evalcheck), an MIT-licensed pytest plugin that handles the snapshot diff for you. You could just as easily roll your own with `pytest` + a JSON file.

## Cells

```python
# Cell 1: pip install
%pip install openai evalcheck pytest
```

```python
# Cell 2: a thing to evaluate
from openai import OpenAI

client = OpenAI()  # uses OPENAI_API_KEY

def summarise(article: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": "Summarise the article in one sentence."},
            {"role": "user", "content": article},
        ],
    )
    return completion.choices[0].message.content
```

```python
# Cell 3: an OpenAI-as-judge metric (homegrown, no third-party tool)
import json

def faithfulness_score(output: str, context: str) -> float:
    """Asks gpt-4o-mini to score whether OUTPUT is faithful to CONTEXT."""
    judgment = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": (
                "Score whether OUTPUT is fully supported by CONTEXT. "
                "1.0 = every claim grounded; 0.0 = invents claims. "
                'Return JSON: {"score": <0-1>, "reasoning": "<one sentence>"}.'
            )},
            {"role": "user", "content": f"Context:\n{context}\n\nOutput:\n{output}"},
        ],
    )
    data = json.loads(judgment.choices[0].message.content)
    return data["score"]
```

```python
# Cell 4: pytest-shaped tests with regression detection
# tests/test_summaries.py
from evalcheck import EvalOutput, eval, faithfulness

ARTICLE = "Paris, the capital of France, sits on the river Seine. The Eiffel Tower is its tallest structure."

@eval(faithfulness, threshold=0.7)
def test_summary_grounded():
    summary = summarise(ARTICLE)
    return EvalOutput(output=summary, context=ARTICLE)
```

```bash
# Cell 5 (markdown): run it
$ pytest                          # writes .evalcheck/results.json
$ evalcheck snapshot --update     # bless the first run as baseline
$ git add .evalcheck && git commit -m "chore: bless eval baseline"
# Future PRs fail if faithfulness drops below baseline - 0.05.
```

## Closing markdown cell

> ### What's happening under the hood
>
> Every `@eval`-decorated test:
>
> 1. Runs the test function as normal pytest.
> 2. Captures the return value (a string or `EvalOutput`).
> 3. Calls the metric — for `faithfulness`, that's the OpenAI-as-judge call shown in Cell 3, just packaged.
> 4. Compares the score against the committed baseline. Fails the test if the drop exceeds `regression_tolerance` (default 0.05).
>
> The pattern is intentionally small — under 200 lines of plumbing in the plugin itself. If you'd rather roll your own without a dependency, the OpenAI-as-judge function in Cell 3 plus a JSON file in your repo is most of it.

## Strategy notes

- **Lead with OpenAI's `response_format: json_object`** — that's the actual hook that makes this notebook useful regardless of evalcheck.
- The third-party plugin is positioned as "convenience layer" not "the point."
- Write the notebook so that even if maintainers ask you to remove the evalcheck dependency entirely, the rest of the notebook is still valuable. Then it can still merge with attribution stripped — and we keep the notebook URL pointing at the pattern, with the plugin link in a "see also" cell at the end.
