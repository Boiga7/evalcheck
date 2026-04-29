# Show HN draft — evalcheck

**Submission URL:** https://news.ycombinator.com/submit
**Submit when:** Tuesday or Wednesday, 7–10am ET (weekday morning gets the most engagement; weekends die fast).
**Don't submit until:** the GitHub App is live and a real PR comment is visible somewhere (Boiga7/evalcheck PR). HN readers click through to verify; an unfinished demo gets buried.

---

## Title (80-char limit)

> Show HN: evalcheck – pytest plugin that catches LLM eval regressions in PRs

(Backup if first dies: "Show HN: PR comments for LLM eval regressions, as a pytest plugin")

## URL

`https://github.com/Boiga7/evalcheck`

## Text body

Built this over the last few weeks of evenings. It scratches a real itch from my day job: every time we change a prompt or swap a model, somebody asks "did quality go up or down" and the honest answer is "I'll run the evals locally and eyeball it."

Coverage tools, bundle-size tools, accessibility checkers — they all show up as PR comments. LLM eval tooling skipped that pattern. evalcheck is a pytest plugin (`pip install evalcheck`, `@eval(faithfulness, threshold=0.7)`) that writes results to `.evalcheck/results.json` after every test run, and a paired GitHub App diffs that against a committed baseline and posts a markdown comment.

A few deliberate choices:

- **Plain `pytest` invocation.** No `deepeval test run`, no `--run-eval` flag, no separate runner. Existing pytest fixtures, `-k` filtering, `pytest-xdist`, IDE integration — all keep working.
- **Baseline lives in git.** No cloud account required. The diff is committable, reviewable, and works in air-gapped CI.
- **Six built-in metrics.** Three LLM-as-judge (faithfulness, relevance, correctness) with OpenAI/Anthropic providers, three deterministic (exact_match, regex_match, custom). Pluggable.

Where it sits relative to other tools: deepeval has more metrics and a polished cloud dashboard but breaks plain `pytest`; pytest-evals is genuinely pytest-native but ships zero metrics; promptfoo is JS-first; braintrust is hosted-only and starts at $249/mo. The wedge is "pytest-native + ships metrics + no cloud + PR comment."

Honest about the state: plugin is on PyPI today (v0.1.0, MIT). The GitHub App half is scaffolded but not yet running on a public webhook URL — that's the next milestone. So right now you can install the plugin and get JSON results out, but the PR comment story isn't live for outsiders yet.

Would love feedback on the API surface in particular. The decorator shape (`@eval(metric, threshold=0.7, **metric_kwargs)`) is opinionated and I'm sure I've gotten something wrong.

---

## After-submission tactics

- Don't reply to the first 3 comments within the first hour. Leave space for organic conversation.
- Do reply to every substantive technical comment within 6 hours.
- Don't argue with criticism. If someone says "this overlaps deepeval," say "yeah, here's specifically where I think the wedge is" and link to the comparison page.
- Don't ask people to upvote. HN is brutal about vote manipulation.
- If it climbs to top 30, keep replying for the next 12 hours. If it dies on page 3 within an hour, leave it — don't bump.

## Avoid in copy

- "AI-powered" anything. HN distrusts the phrase.
- "Game-changing", "next-generation", "revolutionary".
- Long-winded openings about why testing matters. They know.
- Replying to your own post in the first 5 minutes (looks orchestrated).

## Variant for r/MachineLearning (if HN underperforms)

Subreddit values rigour and methodology. Lead with the regression-detection algorithm, the snapshot schema, and an honest comparison table. Less "I built a thing" energy, more "here's a tool that solves X cleanly."
