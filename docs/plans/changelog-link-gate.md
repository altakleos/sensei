---
feature: changelog-link-gate
serves: docs/specs/release-communication.md
design: "Pattern instantiation of the existing ci/check_*.py validator family. No new mechanism — same shape as ci/check_links.py and ci/check_plan_completion.py."
status: done
date: 2026-04-25
---
# Plan: CHANGELOG Link CI Gate

The 2026-04-25 audit Move #2: add a CI validator that prevents CHANGELOG compare-link rot. The 2026-04-25 doc-rot sweep had to repair four missing compare-links (a16–a19) — a gap that survived four releases because the pre-release checklist (`docs/operations/release-playbook.md:160–170`) does not include a link-integrity check, and no validator catches it.

## Targets and Verified Evidence

| # | Target | Evidence |
|---|---|---|
| 1 | `ci/` has no CHANGELOG validator | `fd "changelog" ci/` returns nothing (verified 2026-04-25 against post-merge `main`). |
| 2 | The doc-rot sweep PR #30 had to add four lines | `git log -p main -- CHANGELOG.md` shows the four-line addition in commit `5aaaa85`. |
| 3 | `docs/specs/release-communication.md` declares the changelog the canonical "what changed" artifact | The spec is the load-bearing reason this gap matters. |

## Approach

Add `ci/check_changelog_links.py` modelled on `ci/check_links.py`. Wire into `verify.yml` after `check_links.py`. Add a one-line entry to the pre-release checklist in `release-playbook.md`.

Rules the validator asserts:

1. Every `## [X.Y.Z(suffix)] — YYYY-MM-DD` heading has a matching `[X.Y.Z(suffix)]: <url>` reference-link line at the file tail.
2. The `[Unreleased]:` line compares from the highest-numbered released tag.
3. Each compare URL matches `https://github.com/altakleos/sensei/compare/<from>...<to>` (or, for the very first release, `releases/tag/<tag>`).
4. Reference-link tail entries are sorted descending by version.

Out of scope for the validator: any semantic check on the section bodies (Added/Changed/Fixed). The validator is structural-only, matching the spirit of `ci/check_links.py` (links resolve) and `ci/check_plan_completion.py` (boxes ticked).

## Tasks

- [x] T1 — `ci/check_changelog_links.py`: ≤80 lines. Argparse with `--changelog <path>` (default `CHANGELOG.md`). Returns exit 0 / 1 with JSON-or-prose stderr matching the existing validator family. Public entry: `main(argv: list[str] | None = None) -> int`.
- [x] T2 — `tests/ci/test_check_changelog_links.py`: cases for (a) clean changelog passes; (b) missing compare-link for a heading fails; (c) Unreleased-from mismatch fails; (d) malformed URL fails; (e) non-existent file fails cleanly.
- [x] T3 — `.github/workflows/verify.yml`: add a step `Lint changelog links` after the `Lint markdown links` step, calling `python ci/check_changelog_links.py`.
- [x] T4 — `docs/operations/release-playbook.md`: add a checklist line under "Pre-release Checklist" (line 160–170 region) — `[ ] CHANGELOG compare-links updated for the new tag` — and a one-sentence pointer to the new validator.
- [x] T5 — Run full local pipeline (per `release-playbook.md:13` activation guidance — `.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_*.py`). All green.
- [x] T6 — Commit message: `feat: ci/check_changelog_links.py — gate compare-link integrity`. Single commit on `feat/changelog-link-gate` branch. Open PR.

## Acceptance Criteria

- [x] AC1 — `python ci/check_changelog_links.py` exits 0 against the current `CHANGELOG.md` (post-merge clean state).
- [x] AC2 — Each negative test case in T2 fails with a single-line, file:line-anchored stderr message.
- [x] AC3 — `verify.yml` runs the new step on every push/PR; CI is green on the PR branch.
- [x] AC4 — Pre-release checklist mentions the gate.
- [x] AC5 — `git diff --stat` shows changes only in: `ci/check_changelog_links.py` (added), `tests/ci/test_check_changelog_links.py` (added), `.github/workflows/verify.yml`, `docs/operations/release-playbook.md`, this plan.

## Out of Scope

- Auto-generating compare-links during release. Separate concern.
- Validating section bodies (Added/Changed/Fixed). Structural-only is the agreed shape.
- Backporting the rule to historical `[0.1.0a1]`-style edge cases beyond the existing `releases/tag/<tag>` shape.
- Adding a CHANGELOG entry under `[Unreleased]`. This ships as `feat:` for the new validator but `release-communication.md` says refactors-/internal-tests-/docs-only edits don't need entries; a CI validator counts as internal tooling, not user-visible behavior. Confirm during T6.
