# LlamaIndex cookbook PR draft

**Target repo:** https://github.com/run-llama/llama_index (the `docs/` or `examples/` directory)
**Approach:** mirror the LangChain PR pattern — one tight example notebook showing the regression-tracked CI pattern with LlamaIndex's QueryEngine.

---

## Pre-flight

1. Read https://github.com/run-llama/llama_index/blob/main/CONTRIBUTING.md
2. LlamaIndex maintains examples under `docs/docs/examples/` (Markdown + notebook). Pick the right subfolder — `evaluation/` if it exists.
3. They generally welcome external integrations; tag them clearly.

## PR title

`docs: example for CI eval regression testing with QueryEngine + pytest`

## PR body

> Adds a small example wiring LlamaIndex `QueryEngine` evals into pytest with snapshot-based regression detection. Pattern works in any CI, no SaaS account required.
>
> Built around [evalcheck](https://github.com/Boiga7/evalcheck) — MIT pytest plugin, OSS, judge-as-LLM with OpenAI/Anthropic out of the box. Same approach works with custom evaluators if folks prefer to roll their own; this just shows the shape.
>
> Useful for teams using `llama_index` in production who want a cheap "did the new prompt regress retrieval relevance" gate in their existing pytest CI.

## File: `docs/docs/examples/evaluation/regression_in_ci.md`

```python
# pip install llama-index llama-index-llms-openai evalcheck
from llama_index.core import VectorStoreIndex, Document
from llama_index.llms.openai import OpenAI

documents = [
    Document(text="The Eiffel Tower is in Paris, France."),
    Document(text="The Statue of Liberty is in New York, USA."),
]
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine(llm=OpenAI(model="gpt-4o-mini", temperature=0))
```

```python
# tests/test_retrieval.py — runs under plain `pytest`
from evalcheck import EvalOutput, eval, faithfulness, relevance

QUESTIONS = {
    "eiffel": "Where is the Eiffel Tower?",
    "liberty": "Where is the Statue of Liberty?",
}

@eval(faithfulness, threshold=0.7)
def test_eiffel_grounded():
    response = query_engine.query(QUESTIONS["eiffel"])
    context = "\n".join(n.node.text for n in response.source_nodes)
    return EvalOutput(output=str(response), context=context)

@eval(relevance, threshold=0.7)
def test_liberty_relevant():
    response = query_engine.query(QUESTIONS["liberty"])
    return EvalOutput(output=str(response), input=QUESTIONS["liberty"])
```

End with bash:

```bash
$ pytest                                   # runs evals, writes .evalcheck/results.json
$ evalcheck snapshot --update              # bless current scores as baseline
$ git add .evalcheck && git commit -m "chore: bless eval baseline"
# Subsequent runs fail if relevance/faithfulness drops > 0.05 below baseline.
```

## Why this works for LlamaIndex specifically

LlamaIndex eval framework (`BaseEvaluator`, `FaithfulnessEvaluator`, `RelevancyEvaluator`) is great for in-notebook scoring but doesn't ship a CI integration story. evalcheck slots in as the CI layer without replacing their evaluators — users could even wrap a LlamaIndex evaluator inside a `custom` metric if they want the LlamaIndex prompt templates instead of evalcheck's defaults.

If maintainers push back: offer to credit `FaithfulnessEvaluator` and add a parallel example showing both side-by-side.
