"""LLM-as-judge metrics — faithfulness, relevance, correctness."""

from evalcheck.judge import Judge, make_judge

FAITHFULNESS_SYSTEM = (
    "You are a strict evaluator. Score whether the OUTPUT is fully supported "
    "by the CONTEXT. A score of 1.0 means every claim in the output is "
    "grounded in or directly inferable from the context. A score of 0.0 means "
    "the output contradicts or invents claims not supported by the context. "
    'Return JSON: {"score": <float 0-1>, "reasoning": "<one sentence>"}.'
)

FAITHFULNESS_USER = "Context:\n{context}\n\nOutput:\n{output}"

RELEVANCE_SYSTEM = (
    "You are a strict evaluator. Score whether the OUTPUT is a relevant "
    "answer to the INPUT. A score of 1.0 means the output directly addresses "
    "the input. A score of 0.0 means the output is unrelated or evasive. "
    'Return JSON: {"score": <float 0-1>, "reasoning": "<one sentence>"}.'
)

RELEVANCE_USER = "Input:\n{input}\n\nOutput:\n{output}"

CORRECTNESS_SYSTEM = (
    "You are a strict evaluator. Score whether the ACTUAL output is correct "
    "relative to the EXPECTED answer. Treat semantically equivalent phrasings "
    "as correct. A score of 1.0 means fully correct, 0.0 means wrong. "
    'Return JSON: {"score": <float 0-1>, "reasoning": "<one sentence>"}.'
)

CORRECTNESS_USER = "Expected:\n{expected}\n\nActual:\n{output}"


def faithfulness(output: str, context: str, judge: Judge | None = None) -> float:
    judge = judge or make_judge()
    user = FAITHFULNESS_USER.format(context=context, output=output)
    return judge.score(FAITHFULNESS_SYSTEM, user).score


def relevance(output: str, input: str, judge: Judge | None = None) -> float:
    judge = judge or make_judge()
    user = RELEVANCE_USER.format(input=input, output=output)
    return judge.score(RELEVANCE_SYSTEM, user).score


def correctness(output: str, expected: str, judge: Judge | None = None) -> float:
    judge = judge or make_judge()
    user = CORRECTNESS_USER.format(expected=expected, output=output)
    return judge.score(CORRECTNESS_SYSTEM, user).score
