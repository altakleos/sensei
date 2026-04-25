---
feature: pypi-env-id-resolution
serves: docs/specs/release-process.md
design: "No design doc — pure operational hygiene. Replaces a hardcoded numeric `environment_ids[]` literal in the playbook recipe with a `gh api` resolver that looks up the `pypi` environment's id by name. ADR-0026's body retains the original literal as historical record (immutable per ADR convention); only operational prose changes."
status: done
date: 2026-04-25
---
# Plan: Dynamic Resolution of the `pypi` GitHub Environment ID

ADR-0026 documents the manual-approval recipe with a hardcoded literal: `--field 'environment_ids[]=14342694313'`. The release-playbook (`docs/operations/release-playbook.md:210`) repeats it, and the surrounding prose (line 215) asserts the value is "stable." Both claims are true *today* — but the env-id is GitHub-account state, not source-controlled state. Any operation that recreates the `pypi` environment (account migration, accidental delete + recreate, security rotation) silently breaks every documented `gh api` recipe across the repo. The 2026-04-25 follow-up audit named this as an S-effort surface bug worth pre-emptively closing.

The fix is mechanical: resolve the env-id via `gh api repos/altakleos/sensei/environments/pypi --jq '.id'` and feed the result into the existing approval call. ADR-0026's body retains the original literal as the empirical-witness it always was (immutable per the project's ADR convention); only the operational prose in the playbook changes.

## Tasks

- [x] T1 — Update `docs/operations/release-playbook.md` § "Approving PyPI Publish from the Terminal":
  - Insert a new line in the bash recipe before the existing `gh api .../pending_deployments` POST, resolving `ENV_ID` from the `pypi` environment by name: `ENV_ID=$(gh api repos/altakleos/sensei/environments/pypi --jq '.id')`.
  - Replace the hardcoded `'environment_ids[]=14342694313'` literal in the POST with `"environment_ids[]=$ENV_ID"`.
  - Rewrite the surrounding "the environment ID `14342694313` is stable…" sentence to explain that env-ids are stable across runs but tied to GitHub-account state — recreating the environment changes the id, so resolving by name is the canonical pattern. Note the literal `14342694313` value seen in ADR-0026 was the v0.1.0a20-empirical witness and remains valid only as long as the current `pypi` environment is in place.
  - Add a one-line troubleshooting note: if `gh api .../environments/pypi` returns 404, the environment was deleted or renamed — re-run `docs/plans/release-workflow.md` § Prerequisites to recreate it.
- [x] T2 — No change to `docs/decisions/0026-publish-gate-manual-approval.md`. ADR body is immutable; the literal lives there as historical record. A future archaeologist reading the ADR sees the v0.1.0a20-era id; the playbook is the operational truth.
- [x] T3 — Run the full local pipeline from the project venv: `.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_foundations.py && python ci/check_links.py && python ci/check_links.py --root src/sensei/engine && python ci/check_changelog_links.py && python ci/check_plan_completion.py`. All must stay green.
- [x] T4 — Add row to `docs/plans/README.md` § Shipped index.
- [x] T5 — Commit message: `docs: resolve pypi env-id dynamically in release playbook`. Body cites this plan and the audit recommendation that motivated it.

## Acceptance Criteria

- [x] AC1 — `grep -n "14342694313" docs/operations/release-playbook.md` returns at most one match (a historical pointer in the troubleshooting note, OR zero matches if the rewrite drops the literal entirely). The bash recipe contains zero matches.
- [x] AC2 — `grep -n "ENV_ID" docs/operations/release-playbook.md` returns at least one match in the approval recipe.
- [x] AC3 — `grep -n "environments/pypi" docs/operations/release-playbook.md` returns at least one match (the resolver call).
- [x] AC4 — `grep -n "14342694313" docs/decisions/0026-publish-gate-manual-approval.md` still returns one match (ADR body unchanged — immutability respected).
- [x] AC5 — Full local pipeline (T3) passes.
- [x] AC6 — `git diff --stat` touches only: this plan, `docs/plans/README.md`, `docs/operations/release-playbook.md`. No other files modified.

## Out of Scope

- **Editing ADR-0026's body** to drop or annotate the literal. ADR immutability per AGENTS.md § "Required: Plan Before Build" / `docs/decisions/README.md` rules. If a future GitHub Environment recreation invalidates the literal, the right move is a superseding ADR-0029, not a body edit. This plan does not warrant it: the fix is operational, not a decision reversal.
- **A helper script** (e.g. `scripts/approve-pypi-deployment.sh`) wrapping the resolver + POST. Adds maintenance surface for what fits in five inline shell lines. If the recipe grows further (e.g. adds a confirmation prompt or audit-trail capture) a wrapper becomes worth filing then.
- **Backfilling other repos that fork or vendor the playbook.** No such forks exist today.
- CHANGELOG entry. AGENTS.md: docs-only / process changes don't need one. The user-visible release flow is unchanged; only the maintainer-side recipe evolves.
