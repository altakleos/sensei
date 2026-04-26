---
feature: release-v0.1.0a21
serves: docs/specs/release-process.md
design: "Pattern instantiation of docs/operations/release-playbook.md, exercising the v0.1.0a20 → v0.1.0a21 path. First release with the full ADR-0024 + ADR-0027 + ADR-0028 trio active (audit-log mandatory + 7-test gate breadth + breadth CI-enforced) AND dynamic env-id resolution (ADR-0026 prose follow-up). No new mechanism — the release pipeline IS the release artifact tested."
status: planned
date: 2026-04-26
---
# Plan: Release v0.1.0a21

The `[Unreleased]` CHANGELOG section carries three substantive entries from this session:
- Question-density metric for Tier-1 fixtures (commit `7d76e6c`)
- Teaching-density metric for Tier-1 fixtures (commit `f26c64e`)
- Calibration-anchors spec promoted from draft to accepted (commit `65f19f0`)

This release also exercises the new release-pipeline hardening end-to-end for the first time: ADR-0024 (audit-log mandatory) shipped in v0.1.0a20 and was exercised once; ADR-0027 (gate breadth 3 → 7) and ADR-0028 (breadth CI-enforced) shipped this session and have NEVER fired against a real release. v0.1.0a21 is the first execution of the full trio.

**CHANGELOG scope (maintainer decision, decision #2 at plan-approval time):** The `[0.1.0a21]` section retains ONLY the three existing `[Unreleased]` entries (question_density, teaching_density, calibration-anchors promotion). ADR-0027 + ADR-0028 are release-pipeline-internal — they live in the ADRs themselves and in `docs/operations/release-playbook.md` for archaeology, not in the user-facing CHANGELOG. This narrows the precedent set by v0.1.0a20's ADR-0024 announcement.

## Pre-flight verification (already done before filing this plan)

- `which claude` → `/home/rosantos/.local/bin/claude` ✓
- `CLAUDECODE=1` ✓
- → Per `release-playbook.md` § Pre-release gate "Agent-driven releases" clause, the agent drives the Tier-2 gate end-to-end via Option B (OAuth) without escalating cost-permission asks. Spend mentioned post-run.
- `gh auth status` → logged in as `makutaku` with `repo`, `workflow` scopes ✓
- → Sufficient for tag push, workflow watch, and the `gh api .../pending_deployments` POST.

## Tasks

- [~] T1 — **Skipped (maintainer decision):** no new entries added to `[Unreleased]` before promotion. CHANGELOG `[0.1.0a21]` carries only the three existing entries.
- [ ] T2 — Bump `src/sensei/__init__.py`: `__version__ = "0.1.0a20"` → `"0.1.0a21"`.
- [ ] T3 — Promote `## [Unreleased]` → `## [0.1.0a21] — 2026-04-26`. Add a fresh empty `## [Unreleased]` heading above it.
- [ ] T4 — Update CHANGELOG compare-link tail: bump `[Unreleased]:` to compare from `v0.1.0a21...HEAD`; insert `[0.1.0a21]: https://github.com/altakleos/sensei/compare/v0.1.0a20...v0.1.0a21` immediately below.
- [ ] T5 — Run pre-release Tier-2 gate (7 tests, ~12-14 min, ~$2-4 OAuth via Option B per the agent-driven clause). Capture pytest stdout for the audit log; compute sha256 of the captured stdout for the `transcript_hash` frontmatter field.
- [ ] T6 — Author `docs/operations/releases/v0.1.0a21.md` per the template at `docs/operations/releases/README.md`. Frontmatter: `tag: v0.1.0a21`, `date: 2026-04-26`, `tester: makutaku`, `tool: claude`, `tool_version: <captured>`, `exit_code: 0`, `transcript_hash: <sha256>`. Body MUST list all seven test file paths from `REQUIRED_GATE_TESTS` (ADR-0028 breadth check enforces this).
- [ ] T7 — Run the full local pipeline as a final pre-tag check: `.venv/bin/pytest && .venv/bin/ruff check . && .venv/bin/mypy && python ci/check_foundations.py && python ci/check_links.py && python ci/check_links.py --root src/sensei/engine && python ci/check_changelog_links.py && python ci/check_plan_completion.py && python ci/check_release_audit.py --tag v0.1.0a21`. The audit-log validator MUST pass against the new file.
- [ ] T8 — Add row to `docs/plans/README.md` § Shipped index.
- [ ] T9 — Stage + commit T1-T6 + T8 with message `chore: release v0.1.0a21`. Body lists the [Unreleased] → [0.1.0a21] promotion, the ADR-0027/0028 entries added, the Tier-2 gate's seven-test outcome, and references the audit log file. Push to `origin/main`.
- [ ] T10 — **STOP for confirmation.** Surface the commit SHA and `[0.1.0a21]` CHANGELOG section to the user. Tag only after explicit confirmation. On confirmation: `git tag v0.1.0a21 && git push origin v0.1.0a21`.
- [ ] T11 — Watch the release.yml workflow via `gh run watch`. Verify: pytest matrix (py3.10–3.13) green, build-and-check job green (which now runs check_release_audit.py against the new audit log per ADR-0024 + ADR-0028 — the load-bearing gate of this release), and the publish job pausing at the `pypi` environment for manual approval per ADR-0026.
- [ ] T12 — **STOP for IRREVERSIBLE confirmation.** Once the publish job pauses, surface the run ID + run URL and the `gh api` approval recipe. Do NOT issue the `state=approved` POST without explicit user authorisation per the playbook ("Genuinely irreversible actions — PyPI publish… still require explicit confirmation").
- [ ] T13 — On user authorisation: resolve `ENV_ID` via `gh api repos/altakleos/sensei/environments/pypi --jq '.id'` (per ADR-0026 / commit b006a6d), then `gh api repos/altakleos/sensei/actions/runs/<RUN_ID>/pending_deployments --method POST --field "environment_ids[]=$ENV_ID" --field state=approved --field "comment=Ship it"`. Workflow advances and publishes.
- [ ] T14 — Verify the published artifact: `pip index versions sensei-tutor` should list 0.1.0a21.
- [ ] T15 — Create a GitHub Release for v0.1.0a21 per the playbook (body = the `[0.1.0a21]` CHANGELOG section verbatim + `pip install sensei-tutor==0.1.0a21 --pre` install hint).

## Acceptance Criteria

- [ ] AC1 — `src/sensei/__init__.py` reports `__version__ = "0.1.0a21"`.
- [ ] AC2 — `CHANGELOG.md` has the `[0.1.0a21]` heading dated 2026-04-26 + a new empty `[Unreleased]` heading above it; the `[0.1.0a21]` block contains exactly the three Added/Changed entries that were under `[Unreleased]` at plan-filing time (no ADR-0027/0028 entries — per T1's skip).
- [ ] AC3 — `CHANGELOG.md` compare-link tail has `[0.1.0a21]: ...compare/v0.1.0a20...v0.1.0a21` and `[Unreleased]: ...compare/v0.1.0a21...HEAD`.
- [ ] AC4 — `docs/operations/releases/v0.1.0a21.md` exists; frontmatter conforms to the template; body lists all seven test file paths from `REQUIRED_GATE_TESTS`.
- [ ] AC5 — Tier-2 gate (T5) ran clean: 7 passed, 0 failed, exit 0; the audit log captures the run.
- [ ] AC6 — Full local pipeline (T7) green, including `check_release_audit.py --tag v0.1.0a21`.
- [ ] AC7 — Tag `v0.1.0a21` pushed; `release.yml` triggers.
- [ ] AC8 — `release.yml` verify job passes across py3.10–3.13; build-and-check job passes (audit log + breadth gates green).
- [ ] AC9 — Publish job pauses at the `pypi` GitHub Environment per ADR-0026.
- [ ] AC10 — On explicit user authorisation, the `gh api` approval call returns success; workflow advances; `sensei-tutor==0.1.0a21` appears on PyPI.
- [ ] AC11 — GitHub Release for v0.1.0a21 created.

## Out of Scope

- **A non-aN bump** (v0.1.1, v0.1.0, etc.). Following the established alpha cadence.
- **Yanking any prior release.** v0.1.0a20 stays on PyPI.
- **Re-running v0.1.0a20's release.** Idempotent at the workflow level; PyPI rejects duplicate uploads regardless.
- **A new ADR.** Pure pattern-instantiation of the existing release flow.

## Risk and reversal

- **Pre-tag (T1-T9)**: each step reversible via `git revert <sha>`. Local pipeline is the gate; no remote artifact yet.
- **Post-tag, pre-publish (T10-T12)**: tag deletion via `git tag -d v0.1.0a21 && git push origin :v0.1.0a21` is possible but disruptive (cancels running CI). Acceptable if a problem surfaces between tag and publish.
- **Post-publish (T14+)**: PyPI does NOT allow deletion. Yank is the recovery path per the playbook § Yanking a Bad Release. **T13 is the irreversible step**; the explicit-confirmation gate at T12 exists precisely for this reason.
- **OAuth spend**: ~$2-4 per Tier-2 run. Already covered by the agent-driven clause; no separate ask.

## Notes

If T5 (Tier-2 gate) FAILS on any of the seven tests, this release is blocked. Per the playbook: "A red result means either a protocol prose regression or a schema drift. Do not tag until the gate is green." Surface the failure to the user; investigate before proceeding.

If T6 / T7 / T11 surface a `check_release_audit.py` failure (frontmatter mismatch, breadth gap, etc.) — that's the audit-log gate working as designed. Fix the audit log before re-running.
