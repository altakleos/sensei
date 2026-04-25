---
feature: release-publish-gate-reality
serves: docs/specs/release-process.md
design: "ADR-only correction — ADR-0026 (lite) supersedes ADR-0020. Pattern instantiation of the existing supersession convention (status: superseded + cross-reference). No new mechanism, no schema change, no code change. Documentation is reconciled to observed reality; the spec invariant 'Automatic, un-gated publishes are not permitted' is unchanged and now more obviously satisfied."
status: done
date: 2026-04-25
---
# Plan: Reconcile the Release Publish Gate with Reality

ADR-0020 (`docs/decisions/0020-release-self-bypass.md`) declares the publish gate auto-bypasses for the solo maintainer when `prevent_self_review: false`. `docs/operations/release-playbook.md` § "Self-bypass caveat" extends that claim with a v0.1.0a9 anecdote ("the entire release workflow completed in 1m9s with zero manual approval step"). Empirical reality from the v0.1.0a20 release contradicts both: the publish job paused, `pending_deployments` returned a non-empty list, and `gh api ... pending_deployments --field state=approved` was required to ship. Either GitHub's environment-protection auto-approval semantics changed since 2026-04-21 or the v0.1.0a9 anecdote was misread. Current reality is unambiguous: **manual approval is the canonical step.**

This plan reconciles the docs to observed behaviour. The spec invariant in `docs/specs/release-process.md` ("Automatic, un-gated publishes are not permitted") is unchanged and is now *more* obviously satisfied — the gate does pause, the maintainer does approve. ADR-0020's interpretation ("tag-push counts as approval, the gate skips") is empirically false; ADR-0026 (lite) supersedes it with the corrected interpretation ("the maintainer's `gh api` approval call IS the approval step").

## Tasks

- [x] T1: Write ADR-0026 → `docs/decisions/0026-publish-gate-manual-approval.md`. ADR-lite shape (Decision / Why / Alternative). Decision: the publish gate is a manual approval; the maintainer's `gh api .../pending_deployments --field state=approved` call satisfies the spec invariant; ADR-0020 is superseded. Reference v0.1.0a20 (this release) as the empirical witness. (depends: nothing.)
- [x] T2: Flip ADR-0020 frontmatter `status: accepted` → `status: superseded`. Add `superseded-by: 0026` to the frontmatter. Body untouched per ADR immutability — the original prose remains as historical record of the misinterpretation. (depends: T1.)
- [x] T3: Update `docs/decisions/README.md` — flip ADR-0020 status column to `superseded`; add ADR-0026 row. (depends: T1, T2.)
- [x] T4: Rewrite `docs/operations/release-playbook.md` § "Approving PyPI Publish from the Terminal" to drop the self-bypass framing. The `gh api ... pending_deployments` flow is no longer "only reachable when the gate actually pauses (see caveat)" — it is the canonical step. Delete or rewrite § "Self-bypass caveat" as a historical footnote with a pointer to ADR-0020 → ADR-0026. (depends: T1.)
- [x] T5: Add a row to `docs/plans/README.md` index for this plan. (depends: nothing; runs at the end.)
- [x] T6: No CHANGELOG entry. This is a process / docs reconciliation, not a user-visible behaviour change. The user-visible release flow (push tag → wait briefly → wheel on PyPI) is unchanged.

## Acceptance Criteria

- [x] AC1: `python ci/check_links.py`, `check_foundations.py`, `check_changelog_links.py`, `check_plan_completion.py` all green.
- [x] AC2: `docs/decisions/0020-release-self-bypass.md` status frontmatter is `superseded` and references `0026`. Body is byte-identical to before T2 except for the frontmatter.
- [x] AC3: `docs/decisions/0026-publish-gate-manual-approval.md` exists, ADR-lite shape (≤ 12 body lines), references ADR-0020 as superseded.
- [x] AC4: `docs/decisions/README.md` shows ADR-0020 with status `superseded` and ADR-0026 with status `accepted (lite)` in number order.
- [x] AC5: `docs/operations/release-playbook.md` no longer contains the strings "self-bypass", "auto-approve" / "auto-bypass" used to describe the *current* gate behaviour. Historical reference to those terms (e.g. "previously thought to self-bypass per ADR-0020") is acceptable when accompanied by a pointer to ADR-0026.
- [x] AC6: `.venv/bin/pytest --no-cov` passes (no test regressions; this plan touches no code).
- [x] AC7: `.venv/bin/ruff check .` and `.venv/bin/mypy` are clean.

## Out of Scope

- Reconfiguring the GH Environment to actually auto-approve. The current behaviour (manual approval) is acceptable; the maintainer's approval call is fast and provides a real speed bump that the redundant pre-release gates (Tier-2, audit-log, package-contents, pytest matrix) supplement rather than replace.
- Changing `release-process.md` spec invariants. The spec is unchanged; only the ADR interpretation is.
- Investigating *why* the v0.1.0a9 anecdote claimed 1m9s with no approval. Could be: (a) GitHub semantics changed; (b) the anecdote was wrong; (c) v0.1.0a9 was triggered via a path that bypassed the rule. ADR-0026 documents current reality and stops there; archaeological speculation is not load-bearing.
- Adding a co-reviewer or changing `prevent_self_review` to `true`. Both add latency without adding safety beyond the existing mechanical gates. The maintainer's `gh api` call is sufficient.

## Notes

- ADR immutability per `docs/development-process.md:82` permits flipping `status` to `superseded`; the body of ADR-0020 remains as the archaeological record of the original misinterpretation.
- This plan touches only documentation. No code, no tests, no CI gate changes. The "Plan Before Build" rule still applies because the change touches multiple files and supersedes an accepted ADR.
- After this lands, the release-playbook's pre-release checklist no longer has hidden meaning around the "Approve PyPI Publish" step — it is unambiguously a maintainer action that happens during every release.
