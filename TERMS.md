# Terms of Service

Last updated: 2026-04-29

These terms govern use of the **evalcheck GitHub App**. The pytest plugin (`pip install evalcheck`) is published under the MIT licence in [LICENSE](LICENSE) — its terms are governed by that file alone.

## What evalcheck does

The evalcheck GitHub App receives webhook events from GitHub when CI workflows complete, downloads the `evalcheck-results` artifact your CI uploaded, compares it against the baseline file in your repository, and posts a comment plus a Check status on the relevant pull request. Full details in the [README](README.md) and [PRIVACY](PRIVACY.md).

## Free vs Pro

The free tier covers public repositories and the first 50 evals per private-repo run. The Pro tier ($19 per private repo per month, billed via GitHub Marketplace) lifts the per-run cap and includes priority email support.

GitHub Marketplace handles the payment relationship. Their billing terms apply alongside these.

## Acceptable use

You agree not to:

- Reverse engineer the App in an attempt to bypass plan limits.
- Use the App to evaluate models or content in violation of applicable law (e.g., generating CSAM or material targeting protected groups).
- Submit deliberately malformed payloads to overload the webhook endpoint.

We reserve the right to suspend an installation that violates these terms, with notice via the GitHub Marketplace contact channel.

## No warranty

The App is provided "as is" without warranty of any kind. Eval scores depend on third-party LLM providers (OpenAI, Anthropic, Ollama, etc.), whose availability and behaviour we do not control. Don't use evalcheck as the only quality gate on safety-critical systems.

## Liability

To the extent permitted by law, our total liability for any claim arising from your use of the App is limited to the amount you paid for the App in the 12 months preceding the claim. For free-tier users this means £0.

## Changes

We may update these terms. The "Last updated" date reflects the most recent revision. Material changes will be announced via the GitHub Marketplace listing.

## Contact

Open an issue at https://github.com/Boiga7/evalcheck/issues for any question about these terms.
