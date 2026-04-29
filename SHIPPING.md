# Shipping evalcheck v0.1.0 to PyPI

This is a one-time setup. After it's done, every `git tag vX.Y.Z && git push --tags` ships a new release automatically.

## Prerequisites

- A GitHub account (you have `Boiga7`).
- A PyPI account. Sign up at https://pypi.org/account/register/ if you don't have one. Enable 2FA — PyPI requires it for new uploads.
- The local repo on your machine, ready at `Startups/evalcheck/`.

## Step 1 — Create the GitHub repo

1. Go to https://github.com/new
2. Owner: **Boiga7**, Name: **evalcheck**, Visibility: **Public**.
3. Don't initialize with README, .gitignore, or LICENSE — we already have them.
4. Click **Create repository**.

## Step 2 — Push the local code

In `Startups/evalcheck/`, run:

```bash
git init
git add .
git commit -m "feat: initial v0.1.0 release"
git branch -M main
git remote add origin https://github.com/Boiga7/evalcheck.git
git push -u origin main
```

## Step 3 — Set up PyPI Trusted Publishing (no API token needed)

This is the modern, safer way. PyPI verifies pushes via OIDC from GitHub Actions — no long-lived secret to leak.

1. Log in to https://pypi.org and go to https://pypi.org/manage/account/publishing/
2. Under **Add a new pending publisher**, fill in:
   - **PyPI Project Name:** `evalcheck`
   - **Owner:** `Boiga7`
   - **Repository name:** `evalcheck`
   - **Workflow name:** `release.yml`
   - **Environment name:** `pypi`
3. Click **Add**.

## Step 4 — Create the GitHub `pypi` environment

1. In your `evalcheck` repo on GitHub, go to **Settings → Environments → New environment**.
2. Name it **`pypi`**.
3. (Optional but recommended) Add a deployment branch rule limiting it to tags matching `v*`.
4. Save.

## Step 5 — Tag and push the release

```bash
git tag v0.1.0
git push origin v0.1.0
```

The `Release` workflow fires, builds the sdist + wheel, and publishes to PyPI via OIDC.

Watch it run at: https://github.com/Boiga7/evalcheck/actions

## Step 6 — Verify

Within ~2 minutes of the workflow completing:

```bash
pip install evalcheck
python -c "from evalcheck import eval, exact_match; print('ok')"
```

Then go to https://pypi.org/project/evalcheck/ and confirm the listing looks right (README renders, version is 0.1.0).

## After release

- Add the **PyPI** badge and **Downloads** badge to the README. shields.io URLs:
  - `https://img.shields.io/pypi/v/evalcheck`
  - `https://img.shields.io/pypi/dm/evalcheck`
- The CI workflow runs on every push and PR; tests must pass before merging.
- For the next release, bump `version` in `pyproject.toml` and `evalcheck/__init__.py`, update `CHANGELOG.md`, tag `v0.1.1`, push the tag.

## If something goes wrong

| Problem | Fix |
|---|---|
| Workflow fails: "Trusted publisher not configured" | Re-check Step 3 — workflow name, environment, owner, repo must match exactly. |
| Workflow fails: "package name already exists" | The `evalcheck` name was taken between drafting and publishing. Pick a new name (`pyteval`, `evalmark`), update `pyproject.toml`, redo Step 3 with the new name, retag. |
| Tests fail in CI but pass locally | Likely a Python version mismatch. CI tests 3.10–3.13. Check the matrix in `.github/workflows/ci.yml`. |
| 2FA token issues on PyPI | This setup uses OIDC, not tokens — 2FA only matters for logging in to PyPI's web UI. |

## What this sets up forever

- `git tag vX.Y.Z && git push --tags` ships a new PyPI release.
- Every push and PR runs the test suite on Python 3.10–3.13.
- Coverage gate is `--fail-under=95` in CI; we're at 100% so there's headroom.
