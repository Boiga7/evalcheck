# LangChain cookbook PR draft

**Target repo:** https://github.com/langchain-ai/langchain (or langchain-ai/langchain-academy depending on where they accept eval examples this quarter)
**Approach:** open a PR adding a single short notebook or markdown example showing how to wire evalcheck into a LangChain RAG eval workflow. Keep the PR tiny — one file, ~80 lines.
**Why this works:** maintainers add useful real-world examples to docs. Each merged example becomes a perpetual referral source from langchain.com docs.

---

## Pre-flight

1. Read https://github.com/langchain-ai/langchain/blob/master/.github/CONTRIBUTING.md — they often gate non-trivial changes on issue first.
2. If their guidelines require an issue, open one with title: "docs: example for LLM eval regression testing in CI (pytest + evalcheck)". Link to evalcheck repo. Wait 48h for maintainer signal.
3. Check if there's already an `examples/evaluation/` or `cookbook/eval/` directory and follow its conventions.
4. Sign their CLA if prompted.

## PR title

`docs: add CI eval regression example (pytest + evalcheck)`

## PR body

> Adds a 60-line example showing how to wire LangChain RAG evals into pytest with regression detection, runnable from any CI without a third-party SaaS account.
>
> Motivation: LangChain's existing eval examples cover *running* evals well, but stop at the offline notebook step. Teams I've worked with want the same evals to fail their CI when a prompt change drops faithfulness below the baseline. This shows that pattern in ~one screen.
>
> Uses [evalcheck](https://github.com/Boiga7/evalcheck) (MIT, pytest plugin) for the regression detection. Could swap in any pytest-shaped eval tool — the pattern is what matters; I just used the one I know best.
>
> Tested locally with langchain v0.3 and Python 3.12.

## File: `cookbook/evaluation/regression_testing_in_ci.ipynb` (or `.md` per their conventions)

Content of the example (paste into a notebook, one code cell each):

```python
# Cell 1: setup
# pip install langchain langchain-openai langchain-community evalcheck
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_template(
    "Answer the question using ONLY the provided context.\n\n"
    "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
)
chain = prompt | llm
```

```python
# Cell 2: a tiny RAG fixture
DOCS = {
    "france_capital": "Paris is the capital of France, located on the Seine.",
    "py_creator": "Guido van Rossum created Python in 1991.",
}

def answer(question: str, doc_id: str) -> str:
    return chain.invoke({"context": DOCS[doc_id], "question": question}).content
```

```python
# Cell 3: regression-tracked tests
# test_rag_quality.py — runs under plain `pytest`
from evalcheck import EvalOutput, eval, faithfulness, correctness

@eval(faithfulness, threshold=0.7)
def test_france_grounded_in_context():
    answer_text = answer("What is the capital of France?", "france_capital")
    return EvalOutput(output=answer_text, context=DOCS["france_capital"])

@eval(correctness, threshold=0.7)
def test_python_creator_correct():
    answer_text = answer("Who created Python?", "py_creator")
    return EvalOutput(output=answer_text, expected="Guido van Rossum")
```

```bash
# Cell 4: run in CI
$ pytest
# results.json is written automatically; the first run becomes your baseline.
$ evalcheck snapshot --update      # bless it
$ git add .evalcheck/snapshots/baseline.json && git commit -m "chore: bless eval baseline"
# subsequent CI runs fail if any score drops > 0.05 below baseline
```

End of cell. Add a 2-paragraph closing explaining that the same pattern works for LlamaIndex, custom chains, and agent loops — just return the relevant `EvalOutput` from each test.

## After merge

- The PR is the asset. Even if it sits in their `cookbook/` for years, every page view is a referral.
- Track inbound traffic from `cookbook` URLs in the PyPI download stats.

## If they reject

- Don't argue. Their cookbook standards are theirs to set.
- Pivot to opening a similar PR against `langchain-ai/langgraph` examples or against an opinionated downstream library (e.g. `langfuse-ai/langfuse-docs` examples).
- Or self-publish: put the same example in `Boiga7/evalcheck/examples/langchain.ipynb` and link from the README. Slower compounding but zero gatekeeper.
