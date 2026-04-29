# Examples

Runnable Jupyter notebooks showing evalcheck wired into common LLM stacks. Each one is a copy-pasteable starting point — open in Jupyter (or VS Code's notebook view), set your `OPENAI_API_KEY`, run top to bottom.

| Notebook | What it shows |
|---|---|
| [`langchain_rag.ipynb`](langchain_rag.ipynb) | LangChain RAG chain → faithfulness + correctness in pytest CI. Wraps a LangChain evaluator as a custom metric. |
| [`llamaindex_query_engine.ipynb`](llamaindex_query_engine.ipynb) | LlamaIndex `QueryEngine` → faithfulness + relevance, with the `FaithfulnessEvaluator` wrap pattern. |
| [`openai_judge_in_ci.ipynb`](openai_judge_in_ci.ipynb) | OpenAI `response_format: json_object` for an LLM-as-judge metric. Shows what evalcheck does under the hood. |

## Pattern

All three notebooks follow the same shape:

1. Set up an LLM-driven function (a chain, a query engine, a summariser).
2. Define `@eval`-decorated pytest tests that exercise it.
3. Run `pytest`, then `evalcheck snapshot --update` to bless the first run.
4. Commit `.evalcheck/snapshots/baseline.json`.
5. CI fails on subsequent runs if a score drops more than 0.05 below baseline.

Add the [evalcheck GitHub App](https://github.com/apps/evalcheck) to your repo to get the PR comment + check status surface on top.

## Submitting these upstream

These notebooks live here as the canonical examples for evalcheck. They're also written to be submittable as PRs to the upstream cookbooks (`langchain-ai/langchain`, `run-llama/llama_index`, `openai/openai-cookbook`). Drafts of those PRs — including target paths, contribution guidelines, and rejection-fallback plans — live in [`../outreach/`](../outreach/). Open them when ready, one at a time, after building enough GitHub history that the maintainer doesn't read it as drive-by self-promotion.
