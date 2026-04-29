# Security policy

## Supported versions

Only the latest minor release of evalcheck receives security fixes. Patch backports to older minors are considered case-by-case.

| Version | Supported |
|---|---|
| 0.2.x | yes |
| 0.1.x | no — please upgrade to 0.2 |

## Reporting a vulnerability

Please **do not open a public issue** for security reports. Instead, use GitHub's private vulnerability reporting:

1. Go to https://github.com/Boiga7/evalcheck/security/advisories/new
2. Describe the issue and a minimal reproduction.
3. We aim to acknowledge within 7 days and have a fix or mitigation within 30 days for high-severity reports.

Once the fix is released, we publish a GitHub Security Advisory and credit reporters who want to be named.

## Out of scope

- Vulnerabilities in third-party packages (`openai`, `anthropic`, `pytest`, etc.) — please report those upstream.
- Issues where exploitation requires running arbitrary code as the user already (e.g., a malicious test file). The plugin runs your test code by design.
- Reports about the GitHub App's webhook endpoint — those go to the [evalcheck-app repo](https://github.com/Boiga7/evalcheck-app/security/advisories/new) instead.
