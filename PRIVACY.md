# Privacy Policy

Last updated: 2026-04-29

## Summary

evalcheck is two pieces of software:

1. **The pytest plugin** (`pip install evalcheck`) runs entirely on your own machines. We do not collect, transmit, or store any data from it.
2. **The GitHub App** processes webhook events from GitHub and posts comments to your pull requests. It runs on Vercel.

This document describes what the GitHub App handles.

## Data the GitHub App receives

When you install the App on a repository and a workflow run completes, GitHub sends us a webhook event containing:

- The repository owner and name
- The commit SHA and branch
- A list of associated pull requests
- The workflow run ID

We then call the GitHub API on your behalf, scoped to the installation, to:

- Download the `evalcheck-results` artifact your CI uploaded
- Read your `.evalcheck/snapshots/baseline.json` from the PR's base branch
- Post / update a comment on the pull request
- Set a Check Run on the head commit
- (For paid plans) Read the current Marketplace plan attached to the installation

The eval results we read contain test IDs, metric names, scores, and timestamps. We do not read or store the prompts, outputs, contexts, or expected values that produced those scores — those live only inside your test code on your CI runner.

## Data we store

**None.** The GitHub App is stateless. Every webhook is processed in isolation; nothing is written to a database, file, or third-party service after the response is returned. Vercel may retain function invocation logs for diagnostic purposes per their own data retention policy.

We do not use cookies, tracking pixels, or analytics scripts on the App's webhook endpoint.

## Data we share

We do not share any data with third parties. The only external service the App calls is the GitHub API itself, and only with credentials that GitHub minted for your specific installation.

## Your rights

Because the App stores no data, there is nothing to export, delete, or correct. Uninstalling the App from a repository immediately removes our ability to receive any further events from it.

## Marketplace billing

If you subscribe to a paid plan via GitHub Marketplace, GitHub processes the payment and shares the plan name and billing cycle with us via webhook. Stripe Connect handles the underlying card transaction; we never see your card number. Payment dispute resolution goes through GitHub Marketplace support.

## Changes

This policy may be updated. The "Last updated" date at the top reflects the most recent revision. Material changes will be announced in the GitHub Marketplace listing description.

## Contact

Questions? Open an issue at https://github.com/Boiga7/evalcheck/issues with the label "privacy".
