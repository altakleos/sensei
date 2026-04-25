---
feature: ruff-version-skew
serves: docs/specs/release-process.md
design: "Pattern instantiation of the existing release-playbook venv-activation guidance. Same shape as the line at release-playbook.md:13 that already directs the maintainer to use the venv pytest. Extends to ruff/mypy. No new mechanism."
status: done
date: 2026-04-25
---
# Plan: Close the System-vs-Venv Ruff Version Skew

The 2026-04-25 audit Move #4 (recalibrated): during the doc-rot sweep, `ruff check .` failed locally with `UP038` on `review_scheduler.py:53` while CI was green on the same commit. Investigation showed the cause is a system-vs-venv version skew, not a real lint defect:

- System ruff: `0.12.9` (`/usr/local/bin/ruff`) — `UP038` is enabled.
- Venv ruff: `0.15.11` (`.venv/bin/ruff` from `pip install -e '.[dev]'`) — `UP038` removed/renamed; `All checks passed!`.
- pyproject pin: `ruff>=0.4` (loose floor; no upper bound, no behavioural pin).

The risk is not the lint rule itself — it is that **a maintainer running pre-merge gates locally without venv activation gets a different verdict than CI**. The release playbook already documents the venv-activation pattern for pytest (`docs/operations/release-playbook.md:13–14`); this is the same lesson applied to ruff and mypy. Eliminating the discrepancy keeps local pre-merge checks trustworthy and prevents the "looks broken locally, merges green in CI" failure mode (or its inverse, which is more dangerous).

## Targets and Verified Evidence

| # | Target | Evidence (verified 2026-04-25) |
|---|---|---|
| 1 | System ruff and venv ruff disagree on `review_scheduler.py:53` | `ruff --version` → 0.12.9 (UP038 fires); `.venv/bin/ruff --version` → 0.15.11 (passes). Repro depends only on which binary runs. |
| 2 | pyproject ruff pin is loose | `pyproject.toml:23` reads `"ruff>=0.4"`. No upper bound. |
| 3 | Release playbook already establishes the venv-activation pattern for pytest | `docs/operations/release-playbook.md:13` says "Activate the project venv first — `pyproject.toml` sets `addopts = '--cov=…'` …" — same lesson, narrower scope. |

## Approach

Two-pronged, both small:

1. **Documentation:** extend the release-playbook venv-activation guidance from "run pytest from venv" to "run *all* CI gates from venv (pytest, ruff, mypy, ci/check_*.py)." Single-paragraph addition near the existing guidance, not a new section.
2. **Dependency floor:** raise the `ruff` pin in `pyproject.toml` dev extras from `ruff>=0.4` to a floor that matches what CI would today install. Exact floor TBD by T1 below.

Out of scope: pinning an upper bound on ruff. Upper bounds invite stale-toolchain rot more often than they prevent it; the venv-activation discipline is the load-bearing fix.

## Tasks

- [x] T1 — Determine the right ruff floor. Run `pip index versions ruff` (or check what the most recent CI run actually installed). Pick a floor that (a) keeps `UP038` off `(int, float)` patterns, (b) is a recent stable release. Likely `>=0.6` or `>=0.7`. Same exercise for mypy — verify the existing pin (`pyproject.toml`) is sane.
- [x] T2 — `pyproject.toml`: bump the ruff floor in `dev` extras from `ruff>=0.4` to the floor chosen in T1. Add a comment line above naming the reason ("UP038 was removed in ruff 0.15"). If mypy needs a similar bump, do it in the same edit.
- [x] T3 — `docs/operations/release-playbook.md`: extend the existing pre-release-gate paragraph (currently pytest-only at line 13–14) to cover ruff/mypy/ci-validators. Add an explicit one-liner under "Pre-release Checklist" — `[ ] Local pre-merge gates run from the project venv (pytest, ruff, mypy, ci/check_*.py)`.
- [x] T4 — Re-run full local pipeline via `.venv/bin/` to confirm baseline stays green; then run a counter-test by deactivating the venv and confirming a clear failure mode rather than a silent disagreement.
- [x] T5 — Commit on `chore/ruff-version-skew` branch with message `chore: align local ruff/mypy gates with CI via venv guidance + dep floor`. Open PR.

## Acceptance Criteria

- [x] AC1 — `pip install -e '.[dev]'` in a fresh venv resolves a ruff version that does not flag `(int, float)` UP038.
- [x] AC2 — `release-playbook.md` instructs maintainers to run all gates from the venv, not just pytest.
- [x] AC3 — Pre-release checklist gains the venv-gates line.
- [x] AC4 — `.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_*.py` all green.
- [x] AC5 — `git diff --stat` shows changes only in `pyproject.toml`, `docs/operations/release-playbook.md`, and this plan.

## Out of Scope

- Fixing `review_scheduler.py:53`. The line is fine under the ruff version CI uses; rewriting `(int, float)` → `int | float` to placate a stale system ruff is not a real bug fix and would be churn.
- Adding a CI step that pins or asserts ruff version. The matrix install via dev extras already pins what runs in CI; the issue was local-side, not CI-side.
- Adding a CHANGELOG entry. Per AGENTS.md, dependency-floor bumps that don't change user-visible behavior are not user-visible changes.
