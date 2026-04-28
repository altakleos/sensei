# Branch Protection

Recommended GitHub branch protection rules for the `main` branch.

## Settings

Apply these via **Settings → Branches → Add branch protection rule** for `main`:

| Setting | Value | Why |
|---------|-------|-----|
| Require pull request before merging | **Off** | Solo maintainer project — direct push to main is the norm. Enable when adding contributors. |
| Require status checks to pass | **On** | Gate merges on CI. |
| Required checks | `pytest (py3.10)`, `pytest (py3.12)` | Minimum matrix coverage. Add 3.11/3.13 if flaky tests are resolved. |
| Require branches to be up to date | **Off** | Avoids rebase churn on a low-traffic repo. |
| Require signed commits | **Off** | Nice-to-have, not enforced. |
| Include administrators | **On** | Maintainer is not exempt from CI. |
| Allow force pushes | **Off** | Protect commit history. |
| Allow deletions | **Off** | Prevent accidental branch deletion. |

## Tag protection

Tags matching `v*` trigger the release workflow. Protect them:

| Setting | Value |
|---------|-------|
| Tag protection rule pattern | `v*` |
| Who can create | Maintainers only |

This prevents accidental or unauthorized releases.

## Current state

As of v0.2.0a3, branch protection is not configured — the repo relies on CI (`verify.yml`) as the quality gate. These rules codify the existing practice and add guardrails against force-push and tag tampering.

## When to revisit

- **Adding a second contributor**: Enable "Require pull request before merging"
- **After a force-push incident**: Enable signed commits
- **Moving to a GitHub org**: Consider CODEOWNERS for review routing
