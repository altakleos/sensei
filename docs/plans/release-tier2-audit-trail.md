---
feature: release-tier2-audit-trail
serves: docs/specs/release-process.md
design: "Pure documentation artifact + checklist line. No new mechanism, no script, no CI gate. Pattern instantiation of the existing release-playbook checklist convention."
status: done
date: 2026-04-25
---
# Plan: Per-Release Tier-2 E2E Audit Trail

The 2026-04-25 audit Risk #2: the workstation-only Tier-2 behavioural E2E gate (`docs/operations/release-playbook.md:11–36`) has no recorded green-run log per release. The maintainer is the sole owner of "did the gate run?" with no artifact, no tool/version capture, no audit trail. The same maintainer who could miss running the gate is the same one being trusted to confirm it ran. ADR-0020 (release self-bypass for solo maintainer) accepts this trade-off at the publish step; this plan closes the analogous gap one step earlier in the chain.

This is a documentation-shaped fix. No CI gate, no script — those are bigger plans for later. The smallest mitigation is a committed, dated per-release log file.

## Targets and Verified Evidence

| # | Target | Evidence (verified 2026-04-25) |
|---|---|---|
| 1 | `docs/operations/` has no `releases/` subdir | `ls docs/operations/` shows `context-budget.md`, `parallel-agents.md`, `README.md`, `release-playbook.md`, `shim-validation.md`. |
| 2 | The pre-release checklist names the gate but has no audit-trail line | `release-playbook.md:160–172` lists "CI green on `main`", "CHANGELOG promoted", "version bumped" etc. but no record-of-Tier-2-run line. |
| 3 | `release-playbook.md:38` says "Skip only with an explicit CHANGELOG note" — the only fallback if the gate did not run | This is the only existing audit signal and it only fires for explicit skips, not silent ones. |
| 4 | `release-playbook.md:11` documents what the gate does, but not how it gets recorded | "Do not tag until the gate is green" is enforced by maintainer discipline alone. |

## Approach

1. Create a `docs/operations/releases/` directory with a `README.md` that:
   - Explains the purpose of the directory (audit trail for Tier-2 pre-release checks).
   - Provides a template for per-release log entries.
   - Indexes existing entries.
2. Update `release-playbook.md` § Pre-release Checklist with a line referencing the new artifact.
3. Update `release-playbook.md` § Pre-release gate section with a one-paragraph note pointing at where to commit the log.

Forward-looking only — no backfill for v0.1.0a19. The maintainer doesn't have a recorded Tier-2 run output for that release to backfill from. The next release (v0.1.0a20 or later) is when the artifact lands.

## Tasks

- [x] T1 — Create `docs/operations/releases/README.md` with: purpose paragraph, frontmatter template (tag, date, tester, tool, exit code, transcript hash), worked example showing the expected fields, and an empty "## Index" section that future per-release files reference.
- [x] T2 — `docs/operations/release-playbook.md` § Pre-release gate (paragraph at line 11–14): append one sentence — "Capture the output (or a summary + transcript hash) to `docs/operations/releases/<tag>.md` per the template; commit alongside the release tag."
- [x] T3 — `docs/operations/release-playbook.md` § Pre-release Checklist (lines 160–172): add one line — `[ ] Tier-2 E2E run captured to docs/operations/releases/v<X.Y.Z>.md (per docs/operations/releases/README.md template)`.
- [x] T4 — Run full local pipeline via `.venv/bin/`. All green. (Expected — pure docs, no Python touched.)
- [x] T5 — Commit on `docs/release-tier2-audit-trail` branch with message `docs: add per-release Tier-2 E2E audit-trail template`. Open PR.

## Acceptance Criteria

- [x] AC1 — `docs/operations/releases/README.md` exists with the four required template fields (tag, date, tester, tool) plus exit code + transcript hash.
- [x] AC2 — `release-playbook.md` Pre-release Checklist includes the audit-trail capture line.
- [x] AC3 — `release-playbook.md` Pre-release gate paragraph names the artifact path.
- [x] AC4 — `.venv/bin/pytest -q --no-cov && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_*.py` all green.
- [x] AC5 — `git diff --stat` shows changes only in `docs/operations/release-playbook.md`, this plan, and the new `docs/operations/releases/README.md`.

## Out of Scope

- Backfilling v0.1.0a19 (or any earlier release). No saved Tier-2 output exists to backfill from.
- A CI gate that asserts the artifact's existence at tag time. That would belong in `ci/check_package_contents.py` or a new validator and warrants its own plan; the immediate goal is to create the discipline + the surface, not to enforce mechanically yet.
- A script that captures the Tier-2 output automatically. Would be a useful follow-up; out of scope here.
- Any change to the test suite, schema, or protocol prose.
- Any CHANGELOG entry. Per AGENTS.md, "Refactors, internal tests, and docs-only edits don't need a changelog entry."
